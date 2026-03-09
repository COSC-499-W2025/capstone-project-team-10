import json
from pathlib import Path
from typing import Any, Dict, List

import src.param.param as param


class GuiItemsManager:
    """Manager for reading and managing generated items from items.json"""

    def __init__(self):
        self.items_file = Path(param.internal_resume_storage_path) / "index.json"

    def load_items(self) -> List[Dict[str, Any]]:
        """Load all items from items.json"""
        if not self.items_file.exists():
            return []

        try:
            with self.items_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    return loaded
                elif isinstance(loaded, dict) and isinstance(loaded.get("items"), list):
                    return loaded["items"]
        except (json.JSONDecodeError, OSError):
            return []

        return []

    def save_items(self, items: List[Dict[str, Any]]) -> None:
        """Save items to items.json"""
        try:
            with self.items_file.open("w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
        except OSError as e:
            print(f"Error saving items: {e}")

    def get_item_by_index(self, index: int) -> Dict[str, Any] | None:
        """Get a specific item by index"""
        items = self.load_items()
        if 0 <= index < len(items):
            return items[index]
        return None

    def delete_item(self, index: int) -> bool:
        """Delete an item by index"""
        items = self.load_items()
        if 0 <= index < len(items):
            items.pop(index)
            with self.items_file.open("w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
            return True
        return False
