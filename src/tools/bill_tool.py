import json
from typing import Dict, List, Optional


class BillTool:
    """Tool for calculating bills and splitting costs."""

    def __init__(self):
        self.menu = []
        self.orders = {}

    def set_menu(self, menu: list[dict]):
        """Set menu reference for price lookup."""
        self.menu = menu

    def set_orders(self, orders: dict):
        """Set orders reference for cost calculation."""
        self.orders = orders

    def _get_item_price(self, item_id: str) -> int:
        """Get price of a menu item by ID."""
        for item in self.menu:
            if item.get("item_id") == item_id:
                return item.get("price", 0)
        return 0

    def summarize_orders(self) -> dict:
        """
        Summarize all orders with prices.
        Returns: {"orders": [...], "total": int, "status": "success"}
        """
        summary = []
        total = 0

        for user, order_data in self.orders.items():
            item_id = order_data.get("item_id")
            note = order_data.get("note", "")
            price = self._get_item_price(item_id)
            total += price

            # Get item name
            item_name = "Unknown"
            for item in self.menu:
                if item.get("item_id") == item_id:
                    item_name = item.get("name", "Unknown")
                    break

            summary.append(
                {
                    "user": user,
                    "item_id": item_id,
                    "item_name": item_name,
                    "price": price,
                    "note": note,
                    "paid": order_data.get("paid", False),
                }
            )

        return {"orders": summary, "total": total, "count": len(summary), "status": "success"}

    def split_bill(self) -> dict:
        """
        Calculate individual costs for each user.
        Returns: {"total": int, "per_user": {...}}
        """
        per_user = {}
        total = 0

        for user, order_data in self.orders.items():
            item_id = order_data.get("item_id")
            price = self._get_item_price(item_id)
            per_user[user] = price
            total += price

        return {
            "total": total,
            "per_user": per_user,
            "count": len(per_user),
            "status": "success",
        }

    def get_payment_status(self) -> dict:
        """Get payment status for each user."""
        paid = []
        unpaid = []

        for user, order_data in self.orders.items():
            if order_data.get("paid", False):
                paid.append(user)
            else:
                unpaid.append(user)

        return {"paid": paid, "unpaid": unpaid, "total_users": len(self.orders)}
