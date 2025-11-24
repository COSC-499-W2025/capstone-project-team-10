import os
import datetime
import mimetypes
from typing import Optional, Any
import json


class FileAnalysis:
    def __init__(
        self,
        file_path: str,
        file_name: str,
        file_type: str,
        last_modified: str,
        created_time: str,
        extra_data: Optional[Any] = None,
        importance: float = 0.0,
    ) -> None:
        self.file_path: str = file_path
        self.file_name: str = file_name
        self.file_type: str = file_type
        self.last_modified: str = last_modified
        self.created_time: str = created_time
        # self.extra_data: Optional[Any] = extra_data
        self.extra_data = _make_json_safe(extra_data)
        self.importance = importance
    def to_json(self) -> dict:
        return {
            # "file_path": self.file_path,
            # "file_name": self.file_name,
            # "file_type": self.file_type,
            # "last_modified": self.last_modified,
            # "created_time": self.created_time,
            "extra_data": _make_json_safe(self.extra_data),
            # "importance": self.importance,
        }
    

def _make_json_safe(value):
    if isinstance(value, dict):
        return {k: _make_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_make_json_safe(v) for v in value]
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    # fallback: convert to string
    return str(value)

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
        print(f"Getting extra data for file type: {file_type}")
        match file_type:
            # The reason why the case of "pdf" is quite big is becuase fas_PDF returns an object therefore we need to map its attributes to a dictionary
            # so that it is consistent with other file types that return dictionaries.
            case "pdf":
                from src.fas import fas_pdf  
                print("Extracting PDF data...")
                return fas_pdf.extract_pdf_data(file_path)

            case "docx":
                from src.fas import fas_docx
                return fas_docx.extract_docx_data(file_path)
            
            case "odt":
                from src.fas import fas_odt
                return fas_odt.extract_odt_data(file_path)
            
            case "rtf":
                from src.fas import fas_rtf
                return fas_rtf.extract_rtf_data(file_path)
            
            case "xlsx" | "xls":
                from src.fas import fas_excel
                return fas_excel.extract_excel_data(file_path)

            case "psd" | "photoshop":
                from src.fas import fas_photoshop
                return fas_photoshop.extract_photoshop_data(file_path)
            
            case "jpeg" | "jpg" | "png" | "gif" | "webp" | "tiff" | "bmp" | "heif" | "heic" | "avif":
                from src.fas import fas_image_format
                return fas_image_format.analyze_image(file_path)
            
            case "md" | "markdown":
                from src.fas.fas_md import Markdown  # import Markdown wrapper
                md = Markdown(file_path)
                return {
                    "headers": md.get_headers(),
                    "header_hierarchy": md.get_header_hierarchy(),
                    "word_count": md.get_word_counts(),
                    "code_blocks": md.get_code_blocks(),
                    "paragraphs": md.get_paragraphs(),
                }

            case "git":
                # from src.fas import fas_git
                # return fas_git.extract_git_data(file_path)
                #This will enter the grouping and within grouping will go through all files within the git repo and assign them a repo id
                import fas_git_grouping
                git_group = fas_git_grouping.GitGrouping()
                #Currently it only returns the repo_id and files present within the git folder
                return git_group.add_repository(file_path)

            case _:
                # Generic or unsupported type
                return None

    except ModuleNotFoundError:
        # Handler not implemented yet
        print(f"Error. No handler module found for file type: {file_type}")
        return None
    
def compute_importance(file_type: str, extra_data: Optional[Any]) -> float:
    """
    Returns an importance score for the file.
    Higher score = more important.
    """
    base_scores = {
        "git": 10,
        "pdf": 6,
        "docx": 5,
        "odt": 5,
        "rtf": 4,
        "xlsx": 6,
        "xls": 6,
        "md": 7,  # markdown is often documentation, high importance
        "jpg": 2, "jpeg": 2, "png": 2, "gif": 2,
        "psd": 3,
    }

    # Start with base importance from type
    importance = base_scores.get(file_type.lower(), 1)

    # Boost importance if file contains meaningful content
    try:
        if isinstance(extra_data, dict):
            # Example boosting logic:
            # This need to be changed based on what metrics we use
            importance += extra_data.get("word_count", 0) / 1000
            importance += extra_data.get("page_count", 0) * 0.2
            importance += extra_data.get("table_count", 0) * 0.5
            importance += extra_data.get("image_count", 0) * 0.1
    except:
        pass  # extra_data might not be structured

    return round(float(importance), 2)



def analyze_file(file_path: str) -> Optional[FileAnalysis]:
    file_name = get_file_name(file_path)
    file_type = get_file_type(file_path)
    last_modified = get_last_modified_time(file_path)
    created_time = get_created_time(file_path)
    extra_data = get_file_extra_data(file_path, file_type)
    importance = compute_importance(file_type, extra_data)

    return FileAnalysis(
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        last_modified=last_modified,
        created_time=created_time,
        extra_data=extra_data,
        importance=importance,
    )

def analyze_path(file_path: str) -> Optional[FileAnalysis]:
    if not os.path.exists(file_path):
        print(f"Error: Path '{file_path}' does not exist.")
        return None
    # Otherwise treat as a regular file
    return analyze_file(file_path)


def run_fas(file_path: Optional[str] = None) -> Optional[FileAnalysis]:
    return analyze_path(file_path)

def analyze_file_json(file_path: str) -> Optional[FileAnalysis]:
    file_name = get_file_name(file_path)
    file_type = get_file_type(file_path)
    last_modified = get_last_modified_time(file_path)
    created_time = get_created_time(file_path)
    extra_data = get_file_extra_data(file_path, file_type)
    importance = compute_importance(file_type, extra_data)

    return FileAnalysis(
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        last_modified=last_modified,
        created_time=created_time,
        extra_data=extra_data,
        importance=importance,
    ).to_json()

def analyze_path_json(file_path: str) -> Optional[FileAnalysis]:
    if not os.path.exists(file_path):
        print(f"Error: Path '{file_path}' does not exist.")
        return None
    # Otherwise treat as a regular file
    return analyze_file_json(file_path)


def run_fas_json(file_path: Optional[str] = None) -> Optional[FileAnalysis]:
    return analyze_path_json(file_path)


# This is just to run code directly for testing purposes 
# To run fas from command line
# python -m src.fas.fas
if __name__ == "__main__":
    test_path = input("Enter a file path to analyze: ").strip()
    result = run_fas(test_path)
    resultJSON = run_fas_json(test_path)
    if result:
        # print(result.__dict__)   
        print(result)
        print(json.dumps(result.__dict__, indent=2))
    else:
        print("Analysis failed or file not found.")


# File Path for testing:
# PDF: tests\testdata\test_fas\fas_pdf_test.pdf
# Word: tests\testdata\test_fas\fas_docx_test.docx
# ODT: tests\testdata\test_fas\fas_odt_data.odt
# RTF: tests\testdata\test_fas\fas_rtf_data.rtf
# Excel: tests\testdata\test_fas\fas_excel_test.xlsx
# Photoshop: tests\testdata\test_fas\fas_photoshop_test.psd
# Image: tests\testdata\test_fas\fas_image_test.png
# Markdown: tests\testdata\test_md\test_markdown.md