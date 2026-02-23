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

    def _load_index(self) -> dict:
        self._ensure_storage() # Guarantee folder exists before reading
        try:
            with open(self.index_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"next_id": 1, "resumes": {}}

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
            "filename": new_filename,
            "original_name": source_path.name,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
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
        if entry:
            path = self.storage_dir / entry["filename"]
            if path.exists():
                return path
        return None

    def get_all(self, sort_by: str = "date", reverse: bool = True) -> List[Dict]:
        """
        API: GET /resume (List)
        Returns a list of resume objects for the GUI to display.
        """
        index = self._load_index()
        resumes = list(index["resumes"].values())
        
        if sort_by == "date":
            resumes.sort(key=lambda x: x["created_at"], reverse=reverse)
        elif sort_by == "id":
            resumes.sort(key=lambda x: x["id"], reverse=reverse)
            
        return resumes

    def delete(self, resume_id: int) -> bool:
        # API: DELETE /resume/{id}

        index = self._load_index()
        str_id = str(resume_id)
        
        if str_id in index["resumes"]:
            entry = index["resumes"][str_id]
            file_path = self.storage_dir / entry["filename"]
            
            # Delete physical file
            if file_path.exists():
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error deleting file: {e}")
                    return False

            # Delete index entry
            del index["resumes"][str_id]
            self._save_index(index)
            return True
            
        return False
    
manager = ResumeManager()