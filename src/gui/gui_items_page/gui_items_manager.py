import json
from pathlib import Path
from typing import Any, Dict, List

import src.param.param as param


class GuiItemsManager:
    """Manager for reading and managing generated items from resumes index.json."""

    def __init__(self):
        self.items_file = Path(param.program_file_path) / "storage" / "resumes" / "index.json"
        print(f"Items index path: {self.items_file}")

    def _empty_index(self) -> Dict[str, Any]:
        return {"next_id": 1, "resumes": {}}

    def _load_raw_index(self) -> Dict[str, Any]:
        if not self.items_file.exists():
            return self._empty_index()

        try:
            with self.items_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (json.JSONDecodeError, OSError):
            return self._empty_index()

        if not isinstance(loaded, dict):
            return self._empty_index()

        if not isinstance(loaded.get("resumes"), dict):
            loaded["resumes"] = {}

        if not isinstance(loaded.get("next_id"), int):
            loaded["next_id"] = 1

        return loaded

    def _resume_to_item(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        original = resume.get("original", {}) if isinstance(resume.get("original"), dict) else {}
        backup = resume.get("backup", {}) if isinstance(resume.get("backup"), dict) else {}

        metadata = resume.get("metadata", {}) if isinstance(resume.get("metadata"), dict) else {}

        # Legacy fallback support for pre-migration entries.
        legacy_filename = resume.get("filename", "")
        legacy_original_name = resume.get("original_name", "")

        original_name = original.get("name", "") or legacy_original_name
        original_location = original.get("location", "")
        backup_location = backup.get("location", "")
        fallback_backup_name = backup.get("name", "") or legacy_filename

        if backup_location:
            full_path = backup_location
        elif fallback_backup_name:
            full_path = str((self.items_file.parent / fallback_backup_name).resolve())
        elif original_location:
            full_path = original_location
        else:
            full_path = ""

        return {
            "id": resume.get("id"),
            "name": original_name or fallback_backup_name,
            "path": full_path,
            "type": resume.get("type", "") or metadata.get("type", ""),
            "created_at": resume.get("created_date", "") or resume.get("created_at", ""),
            "log": resume.get("source_log", "") or metadata.get("source_log", ""),
        }

    def load_items(self) -> List[Dict[str, Any]]:
        """
        Returns normalized item rows for ItemsPage table from index.json resumes.
        """
        index = self._load_raw_index()
        resumes = index.get("resumes", {})
        if not isinstance(resumes, dict):
            return []

        items = [self._resume_to_item(entry) for entry in resumes.values() if isinstance(entry, dict)]
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items

    def save_items(self, items: List[Dict[str, Any]]) -> None:
        """
        Keep only resumes whose id exists in `items`, preserving index.json schema.
        """
        index = self._load_raw_index()
        resumes = index.get("resumes", {})
        if not isinstance(resumes, dict):
            resumes = {}

        keep_ids = {str(item.get("id")) for item in items if item.get("id") is not None}
        filtered = {rid: entry for rid, entry in resumes.items() if rid in keep_ids}

        index["resumes"] = filtered
        try:
            with self.items_file.open("w", encoding="utf-8") as f:
                json.dump(index, f, indent=2)
        except OSError as e:
            print(f"Error saving items: {e}")

    def get_item_by_index(self, index: int) -> Dict[str, Any] | None:
        items = self.load_items()
        if 0 <= index < len(items):
            return items[index]
        return None

    def delete_item(self, index: int) -> bool:
        items = self.load_items()
        if not (0 <= index < len(items)):
            return False

        item_id = items[index].get("id")
        if item_id is None:
            return False

        raw = self._load_raw_index()
        resumes = raw.get("resumes", {})
        if not isinstance(resumes, dict):
            return False

        str_id = str(item_id)
        if str_id in resumes:
            del resumes[str_id]
            raw["resumes"] = resumes
            try:
                with self.items_file.open("w", encoding="utf-8") as f:
                    json.dump(raw, f, indent=2)
                return True
            except OSError:
                return False

        return False
