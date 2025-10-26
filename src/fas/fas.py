import os
import datetime
import mimetypes
from typing import Optional, Any

class FileAnalysis:
    def __init__(
        self,
        file_name: str,
        file_type: str,
        last_modified: str,
        created_time: str,
        extra_data: Optional[Any] = None
    ) -> None:
        self.file_name: str = file_name
        self.file_type: str = file_type
        self.last_modified: str = last_modified
        self.created_time: str = created_time
        self.extra_data: Optional[Any] = extra_data


def get_file_type(file_path: str) -> str:
    # First, try to get the file extension
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    if ext:
        return ext

    # Fallback to mimetype
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type.split("/")[-1]

    return "unknown"



def get_last_modified_time(file_path: str) -> str:
    st = os.stat(file_path)
    return datetime.datetime.fromtimestamp(st.st_mtime).isoformat()


def get_created_time(file_path: str) -> str:
    st = os.stat(file_path)
    if hasattr(st, "st_birthtime"):  # macOS
        return datetime.datetime.fromtimestamp(st.st_birthtime).isoformat()
    else:  # Windows/Linux fallback
        return datetime.datetime.fromtimestamp(st.st_ctime).isoformat()


def get_file_name(file_path: str) -> str:
    return os.path.basename(file_path)


def get_file_extra_data(file_path: str, file_type: str) -> Optional[Any]:
    # This is all placeholder and will be replaced when we have proper handlers
    try:
        match file_type:
            case "pdf":
                # from src.fas import fas_pdf
                # return fas_pdf.extract_pdf_data(file_path)
                return None

            case "docx":
                # from src.fas import fas_docx
                # return fas_docx.extract_docx_data(file_path)
                return None

            case "git":
                # from src.fas import fas_git
                # return fas_git.extract_git_data(file_path)
                return None

            case _:
                # Generic or unsupported type
                return None


    except ModuleNotFoundError:
        # Handler not implemented yet
        return None


def analyze_file(file_path: str) -> Optional[FileAnalysis]:
    file_name = get_file_name(file_path)
    file_type = get_file_type(file_path)
    last_modified = get_last_modified_time(file_path)
    created_time = get_created_time(file_path)
    extra_data = get_file_extra_data(file_path, file_type)

    return FileAnalysis(
        file_name=file_name,
        file_type=file_type,
        last_modified=last_modified,
        created_time=created_time,
        extra_data=extra_data
    )
def analyze_path(file_path: str) -> Optional[FileAnalysis]:
    if not os.path.exists(file_path):
        print(f"Error: Path '{file_path}' does not exist.")
        return None

    if os.path.isdir(file_path) and file_path.endswith(".git"):
        # Placeholder for git analysis
        print("Analyzing .git folder (placeholder).")
        return FileAnalysis(
            file_name=".git",
            file_type="git",
            last_modified="N/A",
            created_time="N/A",
            extra_data=None
        )

    # Otherwise treat as a regular file
    return analyze_file(file_path)


def run_fas(file_path: Optional[str] = None) -> Optional[FileAnalysis]:
    return analyze_path(file_path)
