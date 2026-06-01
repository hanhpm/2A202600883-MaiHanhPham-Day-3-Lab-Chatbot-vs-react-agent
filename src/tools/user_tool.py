import json
from pathlib import Path
from typing import List, Dict, Optional


class UserTool:
    """Tool for managing team members and checking order status."""

    def __init__(self, members_path: str = "data/members.json"):
        self.members_path = Path(members_path)
        self.members = self._load_members()

    def _load_members(self) -> list[str]:
        """Load members from JSON file."""
        if not self.members_path.exists():
            return []
        try:
            with self.members_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading members: {e}")
            return []

    def check_missing_orders(self, orders: dict) -> dict:
        """
        Check which members haven't placed orders yet.
        Returns: {"missing": [...], "count": int}
        """
        missing = [member for member in self.members if member not in orders]
        return {"missing": missing, "count": len(missing), "total_members": len(self.members)}

    def check_unpaid(self, orders: dict) -> dict:
        """
        Check which members haven't paid yet.
        Returns: {"unpaid": [...], "count": int}
        """
        unpaid = []
        for user, order_data in orders.items():
            if not order_data.get("paid", False):
                unpaid.append(user)

        return {"unpaid": unpaid, "count": len(unpaid)}

    def get_members(self) -> dict:
        """Get list of all team members."""
        return {"members": self.members, "count": len(self.members)}

    def add_member(self, name: str) -> dict:
        """Add a new team member."""
        if name in self.members:
            return {"status": "error", "message": f"{name} already exists"}
        self.members.append(name)
        return {"status": "success", "message": f"Added {name}", "members": self.members}

    def remove_member(self, name: str) -> dict:
        """Remove a team member."""
        if name not in self.members:
            return {"status": "error", "message": f"{name} not found"}
        self.members.remove(name)
        return {"status": "success", "message": f"Removed {name}", "members": self.members}
