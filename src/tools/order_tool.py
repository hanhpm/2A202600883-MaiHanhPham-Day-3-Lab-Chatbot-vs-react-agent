import json
from typing import Optional, Dict, List


class OrderTool:
    """Tool for managing lunch orders."""

    def __init__(self):
        self.orders = {}  # {user: {"item_id": "M01", "note": "...", "paid": false}}
        self.menu = []

    def set_menu(self, menu: list[dict]):
        """Set menu reference for price lookup."""
        self.menu = menu

    def add_order(self, user: str, item_id: str, note: str = "") -> dict:
        """
        Add a lunch order for a user.
        Returns: {"status": "success|error", "message": "...", "data": {...}}
        """
        if not user or not item_id:
            return {
                "status": "error",
                "message": "user and item_id are required",
                "data": None,
            }

        self.orders[user] = {
            "item_id": item_id,
            "note": note,
            "paid": False,
        }

        return {
            "status": "success",
            "message": f"Order added for {user}",
            "data": {"user": user, "item_id": item_id, "note": note},
        }

    def update_order(self, user: str, item_id: str, note: str = "") -> dict:
        """Update an existing order."""
        if user not in self.orders:
            return {"status": "error", "message": f"No order found for {user}", "data": None}

        self.orders[user] = {
            "item_id": item_id,
            "note": note,
            "paid": self.orders[user].get("paid", False),
        }

        return {
            "status": "success",
            "message": f"Order updated for {user}",
            "data": self.orders[user],
        }

    def get_order(self, user: str) -> Optional[dict]:
        """Get order for a specific user."""
        return self.orders.get(user)

    def list_orders(self) -> dict:
        """List all current orders."""
        return {"orders": self.orders, "count": len(self.orders)}

    def mark_paid(self, user: str) -> dict:
        """Mark an order as paid."""
        if user not in self.orders:
            return {"status": "error", "message": f"No order found for {user}", "data": None}

        self.orders[user]["paid"] = True
        return {"status": "success", "message": f"Marked {user} as paid", "data": self.orders[user]}

    def clear_orders(self):
        """Clear all orders (for new day)."""
        self.orders = {}
        return {"status": "success", "message": "Orders cleared"}
