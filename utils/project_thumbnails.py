import json
import os
from pathlib import Path

import src.param.param as param

def read_json() -> dict:
    """Read the entire metadata JSON from disk."""
    path = Path(os.path.join(param.program_file_path, "storage")) / "project_thumbnail.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not load project metadata: {e}")
        return {}


def write_json(data: dict) -> None:
    """Write metadata dict to disk."""
    path = Path(os.path.join(param.program_file_path, "storage")) / "project_thumbnail.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"Warning: Could not save project metadata: {e}")


def get_thumbnail(project_id: str) -> str:
    """
    Get the thumbnail path for a project.
    Returns the path if it exists on disk, otherwise empty string.
    """
    data = read_json()
    thumb_path = data.get(project_id, {}).get("thumbnail", "")
    if thumb_path and Path(thumb_path).is_file():
        return thumb_path
    return ""


def set_thumbnail(project_id: str, image_path: str) -> bool:
    """
    Set the thumbnail path for a project.
    Returns True on success, False if the file doesn't exist.
    """
    if image_path and not Path(image_path).is_file():
        return False

    data = read_json()
    if project_id not in data:
        data[project_id] = {}
    data[project_id]["thumbnail"] = image_path
    write_json(data)
    return True