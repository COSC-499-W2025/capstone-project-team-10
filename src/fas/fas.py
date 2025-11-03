import os
import datetime
import mimetypes
from typing import Optional, Any


class FileAnalysis:
    def __init__(
        self,
        file_path: str,
        file_name: str,
        file_type: str,
        last_modified: str,
        created_time: str,
        extra_data: Optional[Any] = None,
    ) -> None:
        self.file_path: str = file_path
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
        print(f"Getting extra data for file type: {file_type}")
        match file_type:
            # The reason why the case of "pdf" is quite big is becuase fas_PDF returns an object therefore we need to map its attributes to a dictionary
            # so that it is consistent with other file types that return dictionaries.
            case "pdf":
                import fas_pdf  
                print("Extracting PDF data...")
                pdf_reader = fas_pdf.PDFReader(file_path)
                # Return a dictionary of relevant PDF info
                return {
                    "author": pdf_reader.author,
                    "creator": pdf_reader.creator,
                    "producer": pdf_reader.producer,
                    "title": pdf_reader.title,
                    "subject": pdf_reader.subject,
                    "keywords": pdf_reader.keywords,
                    "page_count": pdf_reader.page_count,
                    "word_count": pdf_reader.word_count,
                    "line_count": pdf_reader.line_count,
                    "char_count": pdf_reader.char_count,
                    "table_count": pdf_reader.table_count,
                    "tables": pdf_reader.tables,
                    "image_count": pdf_reader.image_count,
                    # "images": pdf_reader.images,
                    "link_count": pdf_reader.link_count,
                    "links": pdf_reader.links,
                }

            case "docx":
                # from src.fas import fas_docx
                # return fas_docx.extract_docx_data(file_path)
                return None
            
            case "xlsx" | "xls":
                import fas_excel
                return fas_excel.extract_excel_data(file_path)

            case "git":
                # from src.fas import fas_git
                # return fas_git.extract_git_data(file_path)
                return None

            case _:
                # Generic or unsupported type
                return None

    except ModuleNotFoundError:
        # Handler not implemented yet
        print(f"Error. No handler module found for file type: {file_type}")
        return None


def analyze_file(file_path: str) -> Optional[FileAnalysis]:
    file_name = get_file_name(file_path)
    file_type = get_file_type(file_path)
    last_modified = get_last_modified_time(file_path)
    created_time = get_created_time(file_path)
    extra_data = get_file_extra_data(file_path, file_type)

    return FileAnalysis(
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        last_modified=last_modified,
        created_time=created_time,
        extra_data=extra_data,
    )

def analyze_path(file_path: str) -> Optional[FileAnalysis]:
    if not os.path.exists(file_path):
        print(f"Error: Path '{file_path}' does not exist.")
        return None

    if os.path.isdir(file_path) and file_path.endswith(".git"):
        # Placeholder for git analysis
        print("Analyzing .git folder (placeholder).")
        return FileAnalysis(
            file_path=file_path,
            file_name=".git",
            file_type="git",
            last_modified="N/A",
            created_time="N/A",
            extra_data=None,
        )

    # Otherwise treat as a regular file
    return analyze_file(file_path)


def run_fas(file_path: Optional[str] = None) -> Optional[FileAnalysis]:
    return analyze_path(file_path)


# This is just to run code directly for testing purposes 
if __name__ == "__main__":
    test_path = input("Enter a file path to analyze: ").strip()
    result = run_fas(test_path)
    if result:
        print(result.__dict__)
    else:
        print("Analysis failed or file not found.")
