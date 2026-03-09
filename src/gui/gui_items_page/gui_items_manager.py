import json
from pathlib import Path
from typing import Any, Dict, List

import src.param.param as param


class GuiItemsManager:
    """Manager for reading and managing generated items from index.json"""

    def __init__(self):
        self.items_file = Path(param.internal_resume_storage_path) / "index.json"

    def _load_index(self) -> Dict[str, Any]:
        if not self.items_file.exists():
            return {"resumes": {}}

        try:
            with self.items_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    resumes = loaded.get("resumes", {})
                    if isinstance(resumes, dict):
                        return {"resumes": resumes}
        except (json.JSONDecodeError, OSError):
            pass

        return {"resumes": {}}

    def load_items(self) -> List[Dict[str, Any]]:
        """Load all items from index.json and map to GUI row format."""
        resumes = self._load_index().get("resumes", {})

        items: List[Dict[str, Any]] = []
        for _, resume in resumes.items():
            if not isinstance(resume, dict):
                continue

            filename = resume.get("filename", "")
            full_path = str(Path(param.internal_resume_storage_path) / filename) if filename else ""

            items.append(
                {
                    "id": resume.get("id"),
                    "filename": filename,
                    "name": resume.get("original_name", filename),
                    "type": resume.get("metadata", {}).get("type", ""),
                    "path": full_path,
                    "created_at": resume.get("created_at", ""),
                    "log": resume.get("metadata", {}).get("source_log", ""),
                }
            )

        items.sort(key=lambda x: (x.get("id") is None, x.get("id")))
        return items

    def save_items(self, items: List[Dict[str, Any]]) -> None:
        """Save GUI items back into index.json schema."""
        resumes: Dict[str, Dict[str, Any]] = {}

        for item in items:
            item_id = item.get("id")
            if not isinstance(item_id, int):
                continue

            filename = item.get("filename") or Path(item.get("path", "")).name
            resumes[str(item_id)] = {
                "id": item_id,
                "filename": filename,
                "original_name": item.get("name", filename),
                "created_at": item.get("created_at", ""),
                "metadata": {
                    "type": item.get("type", ""),
                    "source_log": item.get("log", ""),
                },
            }

        try:
            self.items_file.parent.mkdir(parents=True, exist_ok=True)
            with self.items_file.open("w", encoding="utf-8") as f:
                json.dump({"resumes": resumes}, f, indent=2)
        except OSError as e:
            print(f"Error saving items: {e}")

    def get_item_by_index(self, index: int) -> Dict[str, Any] | None:
        items = self.load_items()
        if 0 <= index < len(items):
            return items[index]
        return None

    def delete_item(self, index: int) -> bool:
        items = self.load_items()
        if 0 <= index < len(items):
            items.pop(index)
            self.save_items(items)
            return True
        return False
