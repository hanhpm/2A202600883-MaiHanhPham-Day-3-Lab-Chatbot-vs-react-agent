import json
from pathlib import Path
from typing import Optional, List


class MenuTool:
    """Tool for searching menu items."""

    def __init__(self, menu_path: str = "data/menu.json"):
        self.menu_path = Path(menu_path)
        self.menu = self._load_menu()

    def _load_menu(self) -> list[dict]:
        """Load menu from JSON file."""
        if not self.menu_path.exists():
            return []
        try:
            with self.menu_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading menu: {e}")
            return []

    def search_menu(
        self,
        max_price: Optional[int] = None,
        spicy: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> dict:
        """
        Search menu items based on filters.
        Returns: {"items": [...], "count": int}
        """
        results = []

        for item in self.menu:
            if not item.get("available", True):
                continue

            if max_price is not None and item.get("price", 0) > max_price:
                continue

            if spicy is not None and item.get("spicy") != spicy:
                continue

            if category is not None and item.get("category") != category:
                continue

            results.append(item)

        return {"items": results, "count": len(results)}

    def get_item_by_id(self, item_id: str) -> Optional[dict]:
        """Get a specific menu item by ID."""
        for item in self.menu:
            if item.get("item_id") == item_id:
                return item
        return None
