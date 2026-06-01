"""
Tests for all tools: menu, order, bill, user tools.
"""

import pytest
import json
from pathlib import Path
from src.tools.menu_tool import MenuTool
from src.tools.order_tool import OrderTool
from src.tools.bill_tool import BillTool
from src.tools.user_tool import UserTool


@pytest.fixture
def menu_tool():
    """Fixture for MenuTool."""
    return MenuTool(menu_path="data/menu.json")


@pytest.fixture
def order_tool():
    """Fixture for OrderTool."""
    tool = OrderTool()
    menu_data = json.loads(Path("data/menu.json").read_text())
    tool.set_menu(menu_data)
    return tool


@pytest.fixture
def bill_tool():
    """Fixture for BillTool."""
    tool = BillTool()
    menu_data = json.loads(Path("data/menu.json").read_text())
    tool.set_menu(menu_data)
    return tool


@pytest.fixture
def user_tool():
    """Fixture for UserTool."""
    return UserTool(members_path="data/members.json")


class TestMenuTool:
    """Tests for MenuTool."""

    def test_load_menu(self, menu_tool):
        """Test loading menu from file."""
        assert len(menu_tool.menu) > 0
        assert menu_tool.menu[0]["item_id"] == "M01"

    def test_search_menu_by_price(self, menu_tool):
        """Test searching menu by max price."""
        result = menu_tool.search_menu(max_price=50000)
        assert result["count"] > 0
        assert all(item["price"] <= 50000 for item in result["items"])

    def test_search_menu_by_spicy(self, menu_tool):
        """Test searching menu by spicy level."""
        result = menu_tool.search_menu(spicy=False)
        assert result["count"] > 0
        assert all(not item["spicy"] for item in result["items"])

    def test_search_menu_by_category(self, menu_tool):
        """Test searching menu by category."""
        result = menu_tool.search_menu(category="rice")
        assert result["count"] > 0
        assert all(item["category"] == "rice" for item in result["items"])

    def test_get_item_by_id(self, menu_tool):
        """Test getting a specific menu item."""
        item = menu_tool.get_item_by_id("M01")
        assert item is not None
        assert item["name"] == "Cơm gà"
        assert item["price"] == 45000

    def test_search_unavailable_items(self, menu_tool):
        """Test that unavailable items are excluded."""
        result = menu_tool.search_menu()
        # M05 (Mì ý) is unavailable, should not be in results
        item_ids = [item["item_id"] for item in result["items"]]
        assert "M05" not in item_ids


class TestOrderTool:
    """Tests for OrderTool."""

    def test_add_order(self, order_tool):
        """Test adding an order."""
        result = order_tool.add_order("Minh", "M01", note="ít cơm")
        assert result["status"] == "success"
        assert order_tool.orders["Minh"]["item_id"] == "M01"

    def test_add_order_missing_user(self, order_tool):
        """Test adding order without user fails."""
        result = order_tool.add_order("", "M01")
        assert result["status"] == "error"

    def test_update_order(self, order_tool):
        """Test updating an order."""
        order_tool.add_order("Minh", "M01")
        result = order_tool.update_order("Minh", "M02", note="no onion")
        assert result["status"] == "success"
        assert order_tool.orders["Minh"]["item_id"] == "M02"

    def test_get_order(self, order_tool):
        """Test getting an order."""
        order_tool.add_order("Minh", "M01")
        order = order_tool.get_order("Minh")
        assert order is not None
        assert order["item_id"] == "M01"

    def test_list_orders(self, order_tool):
        """Test listing all orders."""
        order_tool.add_order("Minh", "M01")
        order_tool.add_order("Hạnh", "M02")
        result = order_tool.list_orders()
        assert result["count"] == 2

    def test_mark_paid(self, order_tool):
        """Test marking an order as paid."""
        order_tool.add_order("Minh", "M01")
        result = order_tool.mark_paid("Minh")
        assert result["status"] == "success"
        assert order_tool.orders["Minh"]["paid"] == True

    def test_clear_orders(self, order_tool):
        """Test clearing all orders."""
        order_tool.add_order("Minh", "M01")
        order_tool.clear_orders()
        assert len(order_tool.orders) == 0


class TestBillTool:
    """Tests for BillTool."""

    def test_summarize_orders(self, bill_tool, order_tool):
        """Test summarizing orders."""
        order_tool.add_order("Minh", "M01")  # 45k
        order_tool.add_order("Hạnh", "M02")  # 50k
        bill_tool.set_orders(order_tool.orders)

        result = bill_tool.summarize_orders()
        assert result["status"] == "success"
        assert result["count"] == 2
        assert result["total"] == 95000

    def test_split_bill(self, bill_tool, order_tool):
        """Test splitting bill."""
        order_tool.add_order("Minh", "M01")  # 45k
        order_tool.add_order("Hạnh", "M02")  # 50k
        bill_tool.set_orders(order_tool.orders)

        result = bill_tool.split_bill()
        assert result["status"] == "success"
        assert result["total"] == 95000
        assert result["per_user"]["Minh"] == 45000
        assert result["per_user"]["Hạnh"] == 50000

    def test_get_payment_status(self, bill_tool, order_tool):
        """Test getting payment status."""
        order_tool.add_order("Minh", "M01")
        order_tool.add_order("Hạnh", "M02")
        order_tool.mark_paid("Minh")
        bill_tool.set_orders(order_tool.orders)

        result = bill_tool.get_payment_status()
        assert "Minh" in result["paid"]
        assert "Hạnh" in result["unpaid"]


class TestUserTool:
    """Tests for UserTool."""

    def test_load_members(self, user_tool):
        """Test loading members from file."""
        assert len(user_tool.members) > 0
        assert "Minh" in user_tool.members

    def test_check_missing_orders(self, user_tool, order_tool):
        """Test checking who hasn't ordered."""
        order_tool.add_order("Minh", "M01")
        result = user_tool.check_missing_orders(order_tool.orders)
        assert result["count"] > 0
        assert "Hạnh" in result["missing"]

    def test_check_unpaid(self, user_tool, order_tool):
        """Test checking who hasn't paid."""
        order_tool.add_order("Minh", "M01")
        order_tool.add_order("Hạnh", "M02")
        order_tool.mark_paid("Minh")

        result = user_tool.check_unpaid(order_tool.orders)
        assert "Minh" not in result["unpaid"]
        assert "Hạnh" in result["unpaid"]

    def test_get_members(self, user_tool):
        """Test getting all members."""
        result = user_tool.get_members()
        assert result["count"] > 0
        assert isinstance(result["members"], list)
