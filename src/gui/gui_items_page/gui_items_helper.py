import json
from datetime import datetime
from pathlib import Path


def append_generated_item(generated_file_path: str, file_type: str, log_file: str = None) -> None:
    """
      Helper for .json entry generation
    """
    items_path = Path(__file__).resolve().parent / "items.json"
    items_path.parent.mkdir(parents=True, exist_ok=True)

    generated = Path(generated_file_path)
    entry = {
        "name": generated.stem,
        "path": str(generated.resolve()),
        "type": file_type,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    
    if log_file:
        entry["log"] = str(Path(log_file).resolve())

    data = []
    if items_path.exists():
        try:
            with items_path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    data = loaded
                elif isinstance(loaded, dict) and isinstance(loaded.get("items"), list):
                    data = loaded["items"]
        except (json.JSONDecodeError, OSError):
            data = []

    data.append(entry)

    with items_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)