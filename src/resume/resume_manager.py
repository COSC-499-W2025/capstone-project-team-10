import json
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import src.param.param as param

class ResumeManager:
    def __init__(self):
        # We no longer evaluate the path here to prevent early execution bugs
        pass

    @property
    def storage_dir(self) -> Path:
        # Dynamically grabs the Application Data folder AFTER param.init() runs
        return Path(param.program_file_path) / "storage" / "resumes"

    @property
    def index_file(self) -> Path:
        return self.storage_dir / "index.json"

    def _ensure_storage(self):
        """this creates storage directory and index file if they do not exist"""
        if not self.storage_dir.exists():
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.index_file.exists():
            # Create a default index file
            with open(self.index_file, "w") as f:
                json.dump({"next_id": 1, "resumes": {}}, f, indent=4)

    def _normalize_entry(self, entry: dict) -> dict:
        """Normalize old and partially-formed entries into the current schema."""
        if not isinstance(entry, dict):
            return {}

        normalized = dict(entry)

        # Migrate legacy fields.
        if "created_date" not in normalized and "created_at" in normalized:
            normalized["created_date"] = normalized.get("created_at", "")

        if "type" not in normalized:
            metadata = normalized.get("metadata", {})
            if isinstance(metadata, dict):
                normalized["type"] = metadata.get("type", "")

        if "source_log" not in normalized:
            metadata = normalized.get("metadata", {})
            if isinstance(metadata, dict):
                normalized["source_log"] = metadata.get("source_log", "")

        if "original" not in normalized or not isinstance(normalized.get("original"), dict):
            normalized["original"] = {
                "name": normalized.get("original_name", ""),
                "location": "",
            }

        if "backup" not in normalized or not isinstance(normalized.get("backup"), dict):
            filename = normalized.get("filename", "")
            backup_location = ""
            if filename:
                backup_location = str((self.storage_dir / filename).resolve())
            normalized["backup"] = {
                "name": filename,
                "location": backup_location,
            }

        # Ensure canonical keys always exist.
        normalized.setdefault("created_date", "")
        normalized.setdefault("type", "")
        normalized.setdefault("source_log", "")
        normalized.setdefault("original", {"name": "", "location": ""})
        normalized.setdefault("backup", {"name": "", "location": ""})

        return normalized

    def _normalize_index(self, data: dict) -> tuple[dict, bool]:
        """Normalize index root and entries; returns normalized data and whether changes were made."""
        changed = False

        if not isinstance(data, dict):
            return {"next_id": 1, "resumes": {}}, True

        index = dict(data)

        if not isinstance(index.get("next_id"), int):
            index["next_id"] = 1
            changed = True

        resumes = index.get("resumes")
        if not isinstance(resumes, dict):
            resumes = {}
            changed = True

        normalized_resumes: dict[str, dict] = {}
        for key, value in resumes.items():
            normalized_entry = self._normalize_entry(value)
            if normalized_entry != value:
                changed = True
            normalized_resumes[str(key)] = normalized_entry

        index["resumes"] = normalized_resumes

        # Keep next_id ahead of existing ids.
        max_id = 0
        for key, value in normalized_resumes.items():
            try:
                key_id = int(key)
                max_id = max(max_id, key_id)
            except (TypeError, ValueError):
                pass
            if isinstance(value, dict):
                try:
                    entry_id = int(value.get("id", 0))
                    max_id = max(max_id, entry_id)
                except (TypeError, ValueError):
                    pass

        if index["next_id"] <= max_id:
            index["next_id"] = max_id + 1
            changed = True

        return index, changed

    def _load_index(self) -> dict:
        self._ensure_storage() # Guarantee folder exists before reading
        try:
            with open(self.index_file, "r") as f:
                loaded = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"next_id": 1, "resumes": {}}

        normalized, changed = self._normalize_index(loaded)
        if changed:
            self._save_index(normalized)
        return normalized

    def _save_index(self, data: dict):
        self._ensure_storage() # Guarantee folder exists before writing
        with open(self.index_file, "w") as f:
            json.dump(data, f, indent=4)

    def create(self, source_path: Path, metadata: dict = None) -> int:
        """
        API: POST /resume
        Copies a generated PDF to internal storage and indexes it
        """
        index = self._load_index()
        resume_id = index["next_id"]
        
        new_filename = f"resume_{resume_id}{source_path.suffix}"
        destination = self.storage_dir / new_filename

        shutil.copy(source_path, destination)

        # Record entry
        entry = {
            "id": resume_id,
            "created_date": datetime.now().isoformat(),
            "type": (metadata or {}).get("type", ""),
            "original": {
                "name": source_path.name,
                "location": str(source_path.resolve()),
            },
            "backup": {
                "name": new_filename,
                "location": str(destination.resolve()),
            },
            "source_log": (metadata or {}).get("source_log", ""),
        }
        
        index["resumes"][str(resume_id)] = entry
        index["next_id"] += 1
        self._save_index(index)
        
        print(f"[ResumeManager] Stored resume {resume_id} internally at {destination}")
        return resume_id

    def get(self, resume_id: int) -> Optional[Path]:
        ## API: GET /resume/{id}
        ##Returns the absolute path to the file.

        index = self._load_index()
        entry = index["resumes"].get(str(resume_id))
        if not entry:
            return None
        backup = entry.get("backup", {}) if isinstance(entry.get("backup"), dict) else {}
        backup_location = backup.get("location", "")
        fallback_backup_name = backup.get("name", "")
        if backup_location:
            full_path = Path(backup_location)
        elif fallback_backup_name:
            full_path = (self.storage_dir / fallback_backup_name).resolve()
        else:
            return None

        if full_path.exists():
            return full_path
        return None

    def get_all(self, sort_by: str = "date", reverse: bool = True) -> List[Dict]:
        """
        API: GET /resume (List)
        Returns a list of resume objects for the GUI to display.
        """
        index = self._load_index()
        resumes = list(index["resumes"].values())
        
        if sort_by == "date":
            resumes.sort(key=lambda x: x.get("created_date", ""), reverse=reverse)
        elif sort_by == "id":
            resumes.sort(key=lambda x: x.get("id", 0), reverse=reverse)
            
        return resumes

    def delete(self, resume_id: int) -> bool:
        # API: DELETE /resume/{id}

        index = self._load_index()
        str_id = str(resume_id)
        
        if str_id in index["resumes"]:
            entry = index["resumes"][str_id]
            backup = entry.get("backup", {}) if isinstance(entry.get("backup"), dict) else {}
            backup_location = backup.get("location", "")
            file_path = Path(backup_location) if backup_location else self.storage_dir / backup.get("name", "")
            if file_path.exists():
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error deleting file: {e}")
                    return False
            del index["resumes"][str_id]
            self._save_index(index)
            return True
            
        return False
    
manager = ResumeManager()