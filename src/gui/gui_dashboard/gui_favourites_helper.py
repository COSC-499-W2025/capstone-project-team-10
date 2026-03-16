import json
import os
from pathlib import Path

import src.param.param as param


def _favourites_path() -> Path:
    return Path(os.path.join(param.program_file_path, "storage")) / "favourites.json"


def _load_raw() -> list[dict]:
    """Return the raw list of favourite dicts from disk, or [] on any error."""
    path = _favourites_path()
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("favourites", [])
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not load favourites: {e}")
        return []


def _save_raw(favourites: list[dict]) -> None:
    """Write the list of favourite dicts to disk."""
    path = _favourites_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"favourites": favourites}, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Warning: Could not save favourites: {e}")

def get_favourites() -> list[dict]:
    """Return all favourites as a list of {"project_id": ..., "log_path": ...} dicts."""
    return _load_raw()


def is_favourite(project_id: str, log_path: str | Path) -> bool:
    """Return True if the (project_id, log_path) pair is already favourited."""
    log_str = str(log_path)
    return any(
        f["project_id"] == project_id and f["log_path"] == log_str
        for f in _load_raw()
    )


def add_favourite(project_id: str, log_path: str | Path) -> bool:
    """
    Add a favourite.  Returns True if it was newly added, False if it already
    existed.
    """
    log_str = str(log_path)
    favourites = _load_raw()
    if any(f["project_id"] == project_id and f["log_path"] == log_str for f in favourites):
        return False
    favourites.append({"project_id": project_id, "log_path": log_str})
    _save_raw(favourites)
    return True


def remove_favourite(project_id: str, log_path: str | Path) -> bool:
    """
    Remove a favourite.  Returns True if something was actually removed.
    """
    log_str = str(log_path)
    favourites = _load_raw()
    new_list = [
        f for f in favourites
        if not (f["project_id"] == project_id and f["log_path"] == log_str)
    ]
    if len(new_list) == len(favourites):
        return False
    _save_raw(new_list)
    return True


def toggle_favourite(project_id: str, log_path: str | Path) -> bool:
    """
    Toggle the favourite state.
    Returns True  if the item is NOW a favourite.
    Returns False if it was removed.
    """
    if is_favourite(project_id, log_path):
        remove_favourite(project_id, log_path)
        return False
    else:
        add_favourite(project_id, log_path)
        return True