import ast
import csv
import json
import logging
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, Optional

from fpdf import FPDF
from fpdf.enums import XPos, YPos

import src.log.log as log
import src.param.param as param
from src.fas.fas import FileAnalysis
from src.log.log_sorter import LogSorter
from utils.extension_mappings import CODING_FILE_EXTENSIONS as em

# Template for resume entry in PDF
resume_entry_template = """
{project_name} - {project_type}
Date: {created_time} to {last_modified}"""

# Template for each portfolio entry in HTML
portfolio_entry_template = """
<div class='{file_type}'>
  <h2><a href={new_file_path} >{file_name}</a> - {file_type_upper}</h2>
  <h3>Date Active: {created} to {modified}</h3>
  {details}
</div>
<hr/>
"""

# Supported image file types
image_types = [
    "jpeg",
    "jpg",
    "png",
    "gif",
    "webp",
    "tiff",
    "bmp",
    "heif",
    "heic",
    "avif",
]

# Supported collaborative file types
collaborative_types = ["git"]


def format_last_modified(file_analysis: FileAnalysis) -> str:
    if file_analysis.last_modified == "N/A":
        return "Current"
    last_modified = datetime.fromisoformat(file_analysis.last_modified)
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    if last_modified > one_month_ago:
        return "Current"
    else:
        return last_modified.strftime("%Y-%m-%d")


def format_created_time(file_analysis: FileAnalysis) -> str:
    if file_analysis.created_time == "N/A":
        return "N/A"
    created_time = datetime.fromisoformat(file_analysis.created_time)
    return created_time.strftime("%Y-%m-%d")


def clean_text(text):
    text = " ".join(text.split())  # Remove extra spaces
    text = text.replace("\u00a0", " ")  # Replace non-breaking spaces
    return text


def parse_collaborative(file_analysis: FileAnalysis):
    key_skills = []
    extra_data_skills = []
    commits = []
    author = []
    extra_data_raw = file_analysis.extra_data

    # Get key skills of git project
    if isinstance(extra_data_raw, str):
        try:
            parsed = ast.literal_eval(extra_data_raw)
            if isinstance(parsed, dict):
                key_skills = parsed.get("key_skills", []) or []
                extra_data_skills = parsed.get("extra data", []) or []
                commits = parsed.get("commits", []) or []
                author = parsed.get("author", []) or []
        except (ValueError, SyntaxError):
            key_skills = []
            commits = []
    elif isinstance(extra_data_raw, dict):
        key_skills = extra_data_raw.get("key_skills", []) or []
        extra_data_skills = extra_data_raw.get("extra data", []) or []
        commits = extra_data_raw.get("commits", []) or []
        author = extra_data_raw.get("author", []) or []

    total_commits = commits.get("total_commits", 0)
    total_insertions = commits.get("total_insertions", 0)
    total_deletions = commits.get("total_deletions", 0)
    net_change = commits.get("net_change", 0)
    message_analysis_raw = commits.get("message_analysis", "N/A")

    if message_analysis_raw != "N/A":
        if isinstance(message_analysis_raw, str):
            try:
                # Try to parse if it's a string representation of a set
                parsed_set = ast.literal_eval(message_analysis_raw)
                if isinstance(parsed_set, (set, list)):
                    message_analysis = ", ".join(sorted(parsed_set))
                else:
                    message_analysis = message_analysis_raw
            except (ValueError, SyntaxError):
                message_analysis = message_analysis_raw
        elif isinstance(message_analysis_raw, (set, list)):
            message_analysis = ", ".join(sorted(message_analysis_raw))
        else:
            message_analysis = str(message_analysis_raw)
    else:
        message_analysis = "N/A"

    # Extract key_skills from extra_data_skills (which is a list of file dicts)
    all_project_skills = []
    if isinstance(extra_data_skills, list):
        for file_dict in extra_data_skills:
            if isinstance(file_dict, dict):
                file_extra_data = file_dict.get("Extra data", {})
                if isinstance(file_extra_data, dict):
                    file_skills = file_extra_data.get("key_skills", [])
                    if file_skills:
                        all_project_skills.extend(file_skills)

    # Remove duplicates and join
    all_project_skills = list(set(all_project_skills))
    skills_text = (
        ", ".join(key_skills)
        if key_skills
        else file_analysis.file_type.upper() + " Data Analysis"
    )
    project_skills_text = ", ".join(all_project_skills) if all_project_skills else "N/A"

    commit_summary = f"Total Commits: {total_commits} \nTotal Insertions: +{total_insertions} \nTotal Deletions: -{total_deletions} \nNet Change: {net_change} \nCommit objectives: {message_analysis}"
    # If there is more than one author it becomes a collaborative project
    project_text = "Project Contributions: "
    author_text = "Author: "
    if len(author) >= 2:
        project_text = "Collaborative Project Contributions: "
        author_text = "Authors: "

    output_string = f"{author_text} {author} \n{project_text} {skills_text} \nCommit analysis: {commit_summary} \nKey skills demonstrated in this project: {project_skills_text}"
    return output_string


def parse_code_file(file_analysis: FileAnalysis):
    key_skills = []
    extra_data_raw = file_analysis.extra_data
    code_complexity = "Not Available"

    # Convert locally (do not mutate file_analysis.extra_data)
    if isinstance(extra_data_raw, str):
        try:
            parsed = ast.literal_eval(extra_data_raw)
            if isinstance(parsed, dict):
                key_skills = parsed.get("key_skills", []) or []
                complexity = parsed.get("complexity")
                if isinstance(complexity, dict):
                    code_complexity = complexity.get("estimated", "Not Available")
        except (ValueError, SyntaxError):
            # conversion failed: string isn't a valid Python literal dict
            key_skills = []
    elif isinstance(extra_data_raw, dict):
        # In case it's already a dict for some reason, handle it too
        key_skills = extra_data_raw.get("key_skills", []) or []
        complexity = extra_data_raw.get("complexity")
        if isinstance(complexity, dict):
            code_complexity = complexity.get("estimated", "Not Available")

    # Final text to place in PDF
    skills_text = (
        ", ".join(key_skills)
        if key_skills
        else extra_data_raw.get("language") + " Programming"
    )
    return f"Key Skills demonstrated in this project: {skills_text}\nCode Complexity: {code_complexity}"


def parse_markdown_file(file_analysis: FileAnalysis):
    header = ""
    word_count = 0
    code_blocks = []
    paragraphs = []
    extra_data_raw = file_analysis.extra_data

    # Convert locally (do not mutate file_analysis.extra_data)
    if isinstance(extra_data_raw, str):
        try:
            parsed = ast.literal_eval(extra_data_raw)
            if isinstance(parsed, dict):
                header_hierarchy = parsed.get("header_hierarchy", []) or []
                header = header_hierarchy[0] if header_hierarchy else ""
                word_count = parsed.get("word_count", 0)

                # Handle code_blocks which is a string representation of a set
                code_blocks_raw = parsed.get("code_blocks", "")
                if isinstance(code_blocks_raw, str):
                    try:
                        code_blocks = list(ast.literal_eval(code_blocks_raw))
                    except (ValueError, SyntaxError):
                        code_blocks = []
                elif isinstance(code_blocks_raw, (set, list)):
                    code_blocks = list(code_blocks_raw)

                paragraphs = parsed.get("paragraphs", []) or []
        except (ValueError, SyntaxError):
            # conversion failed: string isn't a valid Python literal dict
            header = ""
    elif isinstance(extra_data_raw, dict):
        # In case it's already a dict for some reason, handle it too
        header_hierarchy = extra_data_raw.get("header_hierarchy", []) or []
        header = header_hierarchy[0] if header_hierarchy else ""
        word_count = extra_data_raw.get("word_count", 0)

        code_blocks_raw = extra_data_raw.get("code_blocks", "")
        if isinstance(code_blocks_raw, str):
            try:
                code_blocks = list(ast.literal_eval(code_blocks_raw))
            except (ValueError, SyntaxError):
                code_blocks = []
        elif isinstance(code_blocks_raw, (set, list)):
            code_blocks = list(code_blocks_raw)

        paragraphs = extra_data_raw.get("paragraphs", []) or []

    # Final text to place in PDF
    header_text = header if header else "Markdown Document"
    languages_text = ", ".join(code_blocks) if code_blocks else "No code blocks"
    skills_text = ", ".join(paragraphs) if paragraphs else "Document Analysis"
    return f"Project: {header_text}\nWord Count: {word_count} | Languages: {languages_text}\nKey Skills demonstrated in this project: {skills_text}"



def parse_extra_data(extra_data_raw):
    if isinstance(extra_data_raw, str):
        try:
            parsed = ast.literal_eval(extra_data_raw)
            return parsed if isinstance(parsed, dict) else {}
        except (ValueError, SyntaxError):
            return {}
    elif isinstance(extra_data_raw, dict):
        return extra_data_raw
    return {}


def generate_resume(
    allow_image: bool = True, output_file_path: Optional[Path] = None
) -> Path | None:
    """
    Generates a PDF resume from the log file.
    """
    logging.getLogger("fpdf").setLevel(logging.ERROR)
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    todays_date: str = datetime.now().strftime("%m-%d-%y")
    export_path: Path = Path(param.export_folder_path) / (todays_date + "-resume.pdf")
    file_number: int = 0
    if output_file_path is None:
        while export_path.exists():
            file_number += 1
            export_path = Path(param.export_folder_path) / (
                todays_date + f"-resume-{file_number}.pdf"
            )
    if output_file_path is not None and isinstance(output_file_path, Path):
        export_path = output_file_path

    log_file: Path = Path(log.current_log_file)
    if not export_path.parent.exists():
        print(f"Export folder does not exist: {export_path}")
        return

    def process_image(fa):
        extra_data_dict = parse_extra_data(fa.extra_data)
        project_desc = "Digital Artwork / Image Project"
        image_meta = extra_data_dict.get("image", {})
        img_format = image_meta.get("format")
        if img_format:
            project_desc += f" ({img_format})"
        lines = [f"Artistic Project: {project_desc}"]
        width = image_meta.get("width")
        height = image_meta.get("height")
        if width and height:
            lines.append(f"Image Dimensions: {width} x {height}")
        # Return image path if allowed, so the main function can embed it
        if allow_image:
            lines.append(f"[IMAGE:{fa.file_path}]")
        return lines

    def process_collaborative(fa):
        return [parse_collaborative(fa)]

    def process_office(fa):
        extra_data = parse_extra_data(fa.extra_data)
        key_skills = extra_data.get("key_skills", [])
        summary = extra_data.get("summary", "")
        skills_text = (
            ", ".join(key_skills)
            if key_skills
            else fa.file_type.upper() + " Data Analysis"
        )
        lines = [f"Key Skills demonstrated in this project: {skills_text}"]
        if fa.file_type in ["docx", "odt", "rtf"] and summary:
            lines.append(f"*File Summary: {summary}*")
        return lines

    def process_code(fa):
        return [parse_code_file(fa)]

    def process_psd(fa):
        return ["Artistic Project: Photoshop Project"]

    def process_markdown(fa):
        return [parse_markdown_file(fa)]

    def process_default(fa):
        return [
            f"File type not analyzed. File details: {json.dumps(fa.__dict__, indent=2)}"
        ]

    def get_processor(fa, ext):
        if fa.file_type in image_types:
            return process_image
        if fa.file_type in collaborative_types:
            return process_collaborative
        if fa.file_type in ["xlsx", "xls", "docx", "odt", "rtf"]:
            return process_office
        if ext in em:
            return process_code
        if fa.file_type == "psd":
            return process_psd
        if fa.file_type in ["md", "markdown"]:
            return process_markdown
        return process_default

    try:
        with open(log_file, "r", encoding="utf-8") as lf:
            reader = csv.reader(lf)
            pdf_output = FPDF()
            pdf_output.add_page()
            pdf_output.add_font("Noto", "", "src/showcase/fonts/noto.ttf", uni=True)
            pdf_output.add_font("Noto", "B", "src/showcase/fonts/notob.ttf", uni=True)
            pdf_output.add_font("Noto", "I", "src/showcase/fonts/notoi.ttf", uni=True)
            pdf_output.add_font("Noto", "BI", "src/showcase/fonts/notobi.ttf", uni=True)

            pdf_output.set_font("Noto", "BI", size=14)
            next(reader)  # Skip header row
            for row in reader:
                fa = FileAnalysis(
                    file_path=row[0],
                    file_name=row[1],
                    file_type=row[2],
                    last_modified=row[3],
                    created_time=row[4],
                    extra_data=row[5],
                    importance=float(row[6]) if row[6] else 0.0,
                    customized=row[7].strip().lower() == 'true' if len(row) > 7 else False,
                    project_id=row[8] if len(row) > 8 else None,
                )
                entry_headers = (
                    resume_entry_template.format(
                        project_name=fa.file_name,
                        project_type=fa.file_type.upper(),
                        created_time=format_created_time(fa),
                        last_modified=format_last_modified(fa),
                    )
                    + "\n"
                )
                header_font_size = 18
                for line in entry_headers.splitlines():
                    pdf_output.set_font("Noto", size=header_font_size, style="B")
                    pdf_output.multi_cell(
                        0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                    )
                    header_font_size -= 2

                pdf_output.set_font("Noto", size=12)
                fa.extra_data = clean_text(fa.extra_data)
                _, ext = os.path.splitext(fa.file_path)
                ext = ext.lower()
                processor = get_processor(fa, ext)
                lines = processor(fa)
                for line in lines:
                    # Special handling for image embedding
                    if (
                        isinstance(line, str)
                        and line.startswith("[IMAGE:")
                        and line.endswith("]")
                    ):
                        image_path = line[7:-1]
                        pdf_output.image(image_path, w=100)
                    else:
                        pdf_output.multi_cell(
                            0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                        )
                pdf_output.ln(10)
            pdf_output.output(str(export_path))
            return export_path
    except Exception as e:
        print(f"Something went wrong: {e}")


def generate_portfolio(
    allow_image: bool = True, output_file_path: Optional[Path] = None
) -> Path | None:
    """
    Generates an HTML portfolio and zips it, copying resources as needed.
    """

    todays_date: str = datetime.now().strftime("%m-%d-%y")
    portfolio_export_path_dir: Path = Path(param.export_folder_path) / (
        todays_date + "-portfolio"
    )
    portfolio_export_zip_path_dir: Path = Path(param.export_folder_path) / (
        todays_date + "-portfolio.zip"
    )
    file_number: int = 0

    # Ensure unique folder and zip file names
    while portfolio_export_path_dir.exists() or portfolio_export_zip_path_dir.exists():
        file_number += 1
        portfolio_export_path_dir = Path(param.export_folder_path) / (
            todays_date + f"-portfolio-{file_number}"
        )
        portfolio_export_zip_path_dir = Path(param.export_folder_path) / (
            todays_date + f"-portfolio-{file_number}.zip"
        )

    # Create portfolio and resources directories
    portfolio_export_path_dir.mkdir(parents=True, exist_ok=True)
    portfolio_export_resource_path: Path = portfolio_export_path_dir / "resources"
    portfolio_export_resource_path.mkdir(parents=True, exist_ok=True)

    portfolio_export_path: Path = portfolio_export_path_dir / (
        todays_date + "-portfolio.html"
    )
    log_file: Path = Path(log.current_log_file)
    if not portfolio_export_path_dir.exists():
        print(f"Export folder does not exist: {portfolio_export_path}")
        return

    # --- Handler functions for each file type ---
    def html_image(fa, extra_dict):
        img_meta = extra_dict.get("image", {})
        img_format = img_meta.get("format", "Image")
        width = img_meta.get("width")
        height = img_meta.get("height")
        project_desc = f"Digital Artwork ({img_format})"
        if width and height:
            project_desc += f" — {width} x {height}"
        img_tag = (
            f'<img src="resources/{fa.file_name}.{fa.file_type}" width="300"/>'
            if allow_image
            else ""
        )
        return f"""
            <p><strong>Artistic Project:</strong> {project_desc}</p>
            {img_tag}
        """

    def html_collaborative(fa, extra_dict):
        # You could refactor this to use parse_collaborative if you want
        key_skills = extra_dict.get("key_skills", [])
        extra_data_skills = extra_dict.get("extra data", [])
        commits = extra_dict.get("commits", {})
        author = extra_dict.get("author", [])
        total_commits = commits.get("total_commits", 0)
        total_insertions = commits.get("total_insertions", 0)
        total_deletions = commits.get("total_deletions", 0)
        net_change = commits.get("net_change", 0)
        message_analysis = commits.get("message_analysis", "N/A")
        all_project_skills = []
        if isinstance(extra_data_skills, list):
            for file_dict in extra_data_skills:
                if isinstance(file_dict, dict):
                    file_extra_data = file_dict.get("Extra data", {})
                    if isinstance(file_extra_data, dict):
                        file_skills = file_extra_data.get("key_skills", [])
                        if file_skills:
                            all_project_skills.extend(file_skills)
        all_project_skills = list(set(all_project_skills))
        skills_text = (
            ", ".join(key_skills)
            if key_skills
            else fa.file_type.upper() + " Data Analysis"
        )
        project_skills_text = (
            ", ".join(all_project_skills) if all_project_skills else "N/A"
        )
        commit_summary = f"Total Commits: {total_commits} <br>Total Insertions: +{total_insertions} <br>Total Deletions: -{total_deletions} <br>Net Change: {net_change} <br>Commit objectives: {message_analysis}"
        project_text = "Project Contributions: "
        author_text = "Author: "
        if len(author) >= 2:
            project_text = "Collaborative Project Contributions: "
            author_text = "Authors: "
        return f"""
            <p>{author_text} {author}</p>
            <p><strong>{project_text}</strong></p>
            <pre>{skills_text}</pre>
            <pre>Commit analysis: {commit_summary}</pre>
            <pre>Key skills demonstrated in this project: {project_skills_text}</pre>
        """

    def html_office(fa, extra_dict):
        key_skills = extra_dict.get("key_skills", [])
        summary = extra_dict.get("summary", "")
        skills_text = (
            ", ".join(key_skills)
            if key_skills
            else f"{fa.file_type.upper()} Data Analysis"
        )
        details = f"<p><strong>Key Skills:</strong> {skills_text}</p>"
        if fa.file_type in ("docx", "odt", "rtf") and summary:
            details += f"<p><em>File Summary:</em> {summary}</p>"
        return details

    def html_code(fa, extra_dict, code_type):
        key_skills = extra_dict.get("key_skills", [])
        complexity = extra_dict.get("complexity", {})
        language = extra_dict.get("language", "Programming")
        code_complexity = "Not Available"
        if isinstance(complexity, dict):
            code_complexity = complexity.get("estimated", "Not Available")
        skills_text = ", ".join(key_skills) if key_skills else f"{language} Programming"
        return f"""
            <p><strong>Key Skills:</strong> {skills_text}</p>
            <p><em>Code Complexity:</em> {code_complexity}</p>
        """

    def html_psd(fa, extra_dict):
        width = extra_dict.get("width")
        height = extra_dict.get("height")
        layers = extra_dict.get("number_of_layers")
        psd_desc = "Photoshop Design Project"
        if width and height:
            psd_desc += f" — {width} x {height}"
        if layers:
            psd_desc += f" — {layers} Layers"
        return f"<p><strong>Artistic Project:</strong> {psd_desc}</p>"

    def html_markdown(fa, extra_dict):
        header = extra_dict.get("header_hierarchy", [])
        header_text = header[0] if header else "Markdown Document"
        word_count = extra_dict.get("word_count", 0)
        code_blocks_raw = extra_dict.get("code_blocks", "")
        if isinstance(code_blocks_raw, str):
            try:
                code_blocks = list(ast.literal_eval(code_blocks_raw))
            except (ValueError, SyntaxError):
                code_blocks = []
        elif isinstance(code_blocks_raw, (set, list)):
            code_blocks = list(code_blocks_raw)
        else:
            code_blocks = []
        languages_text = ", ".join(code_blocks) if code_blocks else "No code blocks"
        paragraphs = extra_dict.get("paragraphs", [])
        skills_text = ", ".join(paragraphs) if paragraphs else "Document Analysis"
        return f"""
            <p><strong>Project:</strong> {header_text}</p>
            <p><strong>Word Count:</strong> {word_count} | <strong>Languages:</strong> {languages_text}</p>
            <p><strong>Key Skills:</strong> {skills_text}</p>
        """

    def html_default(fa, extra_dict):
        return f"<p><strong>File type not analyzed. File details: {json.dumps(fa.__dict__, indent=2)}</strong></p>"

    # --- Handler mapping ---
    def get_html_details(fa, extra_dict, code_type):
        ext = fa.file_type
        if ext in image_types:
            return html_image(fa, extra_dict)
        if ext in collaborative_types:
            return html_collaborative(fa, extra_dict)
        if ext in ("xlsx", "xls", "docx", "odt", "rtf"):
            return html_office(fa, extra_dict)
        if code_type in em:
            return html_code(fa, extra_dict, code_type)
        if ext == "psd":
            return html_psd(fa, extra_dict)
        if ext in ("md", "markdown"):
            return html_markdown(fa, extra_dict)
        return html_default(fa, extra_dict)

    try:
        with open(log_file, "r", encoding="utf-8") as lf:
            with open(portfolio_export_path, "w") as portfolio:
                # Write HTML header
                portfolio.write("<html><head><title>Portfolio</title></head><body>\n")
                portfolio.write("<h1>Project Portfolio</h1>\n")
                reader = csv.reader(lf)
                next(reader)  # Skip header row
                for row in reader:
                    file_analysis = FileAnalysis(
                        file_path=row[0],
                        file_name=row[1],
                        file_type=row[2],
                        last_modified=row[3],
                        created_time=row[4],
                        extra_data=row[5],
                        importance=float(row[6]) if row[6] else 0.0,
                        customized=row[7].strip().lower() == 'true' if len(row) > 7 else False,
                        project_id=row[8] if len(row) > 8 else None,
                    )
                    # Copy file to resources folder with correct extension
                    file_analysis_source = Path(file_analysis.file_path)
                    if not file_analysis_source.is_dir():
                        shutil.copy(
                            file_analysis_source,
                            portfolio_export_resource_path
                            / (file_analysis.file_name + "." + file_analysis.file_type),
                        )
                    extra_dict = parse_extra_data(file_analysis.extra_data)
                    _, code_type = os.path.splitext(file_analysis.file_path)
                    code_type = code_type.lower()
                    details = get_html_details(file_analysis, extra_dict, code_type)
                    portfolio.write(
                        portfolio_entry_template.format(
                            new_file_path=f"resources/{file_analysis.file_name}.{file_analysis.file_type}",
                            file_type=file_analysis.file_type,
                            file_name=file_analysis.file_name,
                            file_type_upper=file_analysis.file_type.upper(),
                            created=format_created_time(file_analysis),
                            modified=format_last_modified(file_analysis),
                            details=details,
                        )
                    )
                portfolio.write("</body></html>\n")
        # Zip the portfolio directory and remove the unzipped folder
        shutil.make_archive(
            str(portfolio_export_path_dir), "zip", root_dir=portfolio_export_path_dir
        )
        shutil.rmtree(portfolio_export_path_dir)
        return Path(f"{str(portfolio_export_path_dir)}.zip")
    except Exception as e:
        print(f"Failed to read log file: {e}")
        return


def generate_skill_timeline() -> Path | None:
    """
    Generates a chronological skills timeline from the sorted log file.
    """
    logging.getLogger("fpdf").setLevel(logging.ERROR)
    logging.getLogger("fontTools").setLevel(logging.ERROR)

    todays_date = datetime.now().strftime("%m-%d-%y")
    export_path: Path = Path(param.export_folder_path) / (
        todays_date + "-skills_timeline.pdf"
    )
    file_number: int = 0

    while export_path.exists():
        file_number += 1
        export_path = Path(param.export_folder_path) / (
            f"{todays_date}-skills_timeline-{file_number}.pdf"
        )

    if not log.current_log_file:
        print("No current log file available.")
        return None

    log_file = Path(log.current_log_file)
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        return None

    def extract_skills(extra_data_raw):
        """Extracts a list of skills from the extra_data field."""
        skills = []
        if isinstance(extra_data_raw, dict):
            candidate = extra_data_raw.get("key_skills") or extra_data_raw.get("skills")
            if isinstance(candidate, list):
                skills = [str(s).strip() for s in candidate if str(s).strip()]
            elif isinstance(candidate, str) and candidate.strip():
                skills = [candidate.strip()]
        elif isinstance(extra_data_raw, str):
            text = extra_data_raw.strip()
            if text:
                try:
                    parsed = ast.literal_eval(text)
                except Exception:
                    skills = [clean_text(text)]
                else:
                    if isinstance(parsed, dict):
                        candidate = parsed.get("key_skills") or parsed.get("skills")
                        if isinstance(candidate, list):
                            skills = [
                                str(s).strip() for s in candidate if str(s).strip()
                            ]
                        elif isinstance(candidate, str) and candidate.strip():
                            skills = [candidate.strip()]
                    elif isinstance(parsed, list):
                        skills = [str(s).strip() for s in parsed if str(s).strip()]
                    else:
                        skills = [clean_text(text)]
        return skills

    def format_timeline_date(fa: "FileAnalysis"):
        """Returns a formatted date string for the timeline."""
        date_str = (
            fa.created_time
            if fa.created_time and fa.created_time != "N/A"
            else fa.last_modified
        )
        if date_str and date_str != "N/A":
            try:
                dt = datetime.fromisoformat(date_str)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                return date_str
        return "N/A"

    def write_timeline_entry(pdf, fa, skills):
        """Writes a single timeline entry to the PDF."""
        date_display = format_timeline_date(fa)
        header_line = f"{date_display} - {fa.file_name} ({fa.file_type.upper()})"
        pdf.set_font("Noto", "B", size=12)
        pdf.multi_cell(
            0, 8, clean_text(header_line), new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        pdf.set_font("Noto", "", size=11)
        skills_text = ", ".join(skills)
        pdf.multi_cell(
            0,
            6,
            f"Skills: {clean_text(skills_text)}",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        pdf.ln(3)

    sorter = LogSorter(str(log_file))
    sorter.set_sort_parameters(["Last modified"], [False])
    sorter.sort()
    sorter.return_csv()
    sorted_log_file = log_file.with_name(f"{log_file.stem}_sorted{log_file.suffix}")

    if not export_path.parent.exists():
        print(f"Export folder does not exist: {export_path.parent}")
        return None

    try:
        with open(sorted_log_file, "r", encoding="utf-8", newline="") as lf:
            reader = csv.DictReader(lf)
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font("Noto", "", "src/showcase/fonts/noto.ttf", uni=True)
            pdf.add_font("Noto", "B", "src/showcase/fonts/notob.ttf", uni=True)
            pdf.add_font("Noto", "I", "src/showcase/fonts/notoi.ttf", uni=True)
            pdf.add_font("Noto", "BI", "src/showcase/fonts/notobi.ttf", uni=True)
            pdf.set_font("Noto", "B", size=16)
            pdf.multi_cell(0, 10, "Skill Timeline", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(4)
            next(reader, None)

            for row in reader:
                fa = FileAnalysis(
                    row.get("File path analyzed", ""),
                    row.get("File name", ""),
                    row.get("File type", ""),
                    row.get("Last modified", ""),
                    row.get("Created time", ""),
                    row.get("Extra data", ""),
                    float(row.get("Importance", 0)) if row.get("Importance") else 0.0,
                    row.get("Customized", "").lower() == 'true' if row.get("Customized") else False,
                    row.get("Project id", ""),
                )
                skills = extract_skills(fa.extra_data)
                if not skills:
                    continue
                write_timeline_entry(pdf, fa, skills)

            pdf.output(str(export_path))
            return export_path

    except Exception as e:
        print(f"Failed to generate skills timeline: {e}")
        return None
