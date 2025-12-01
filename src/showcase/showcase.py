import csv
import json
import logging
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import ast

from fpdf import FPDF
from fpdf.enums import XPos, YPos

import src.log.log as log
import src.param.param as param
from src.fas.fas import FileAnalysis

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


def generate_all():
    """
    Generates both the resume and the portfolio.
    """
    generate_resume()
    generate_portfolio()


def generate_resume() -> Path | None:
    """
    Generates a PDF resume from the log file.
    """
    logging.getLogger("fpdf").setLevel(logging.ERROR)
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    todays_date: str = datetime.now().strftime("%m-%d-%y")
    export_path: Path = Path(param.export_folder_path) / (todays_date + "-resume.pdf")
    file_number: int = 0
    # Ensure unique file name by incrementing if file exists
    while export_path.exists():
        file_number += 1
        export_path = Path(param.export_folder_path) / (
            todays_date + f"-resume-{file_number}.pdf"
        )

    log_file: Path = Path(log.current_log_file)
    # Check if export directory exists
    if not export_path.parent.exists():
        print(f"Export folder does not exist: {export_path}")
        return
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
                # Create FileAnalysis object from CSV row
                file_analysis: FileAnalysis = FileAnalysis(
                    row[0], row[1], row[2], row[3], row[4], row[5]
                )
                # Format entry header for this file
                entry_headers: str = (
                    resume_entry_template.format(
                        project_name=file_analysis.file_name,
                        project_type=file_analysis.file_type.upper(),
                        created_time=format_created_time(file_analysis),
                        last_modified=format_last_modified(file_analysis),
                    )
                    + "\n"
                )
                header_font_size: int = 18
                # Write each line of the entry header with decreasing font size
                for line in entry_headers.splitlines():
                    pdf_output.set_font("Noto", size=header_font_size, style="B")
                    pdf_output.multi_cell(
                        0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                    )
                    header_font_size -= 2

                pdf_output.set_font("Noto", size=12)
                # Add details based on file type
                file_analysis.extra_data = clean_text(file_analysis.extra_data)
                _, ext = os.path.splitext(file_analysis.file_path)
                ext = ext.lower()       
                match file_analysis.file_type:
                    case file_type if file_type in image_types:
                        
                        # Convert extra_data to dict if it is a string
                        extra_data_raw = file_analysis.extra_data
                        extra_data_dict = {}

                        if isinstance(extra_data_raw, str):
                            try:
                                extra_data_dict = ast.literal_eval(extra_data_raw)
                            except (ValueError, SyntaxError):
                                extra_data_dict = {}
                        elif isinstance(extra_data_raw, dict):
                            extra_data_dict = extra_data_raw

                        # Basic generic description
                        project_desc = "Digital Artwork / Image Project"

                        # Optionally, include size or format for a bit more info
                        image_meta = extra_data_dict.get("image", {})
                        img_format = image_meta.get("format")
                        if img_format:
                            project_desc += f" ({img_format})"

                        # Short project description
                        pdf_output.multi_cell(
                            0,
                            10,
                            f"Artistic Project: {project_desc}",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )

                        # Image dimensions (optional)
                        image_meta = extra_data_dict.get("image", {})
                        width = image_meta.get("width")
                        height = image_meta.get("height")
                        if width and height:
                            pdf_output.multi_cell(
                                0,
                                10,
                                f"Image Dimensions: {width} x {height}",
                                new_x=XPos.LMARGIN,
                                new_y=YPos.NEXT,
                            )

                        # Embed the image itself
                        pdf_output.image(file_analysis.file_path, w=100)

                    case file_type if file_type in collaborative_types:

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
                        message_analysis_raw= commits.get("message_analysis", "N/A")

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
                        skills_text = ", ".join(key_skills) if key_skills else file_analysis.file_type.upper() + " Data Analysis"
                        project_skills_text = ", ".join(all_project_skills) if all_project_skills else "N/A"

                        commit_summary = f"Total Commits: {total_commits} \nTotal Insertions: +{total_insertions} \nTotal Deletions: -{total_deletions} \nNet Change: {net_change} \nCommit objectives: {message_analysis}"
                        # If there is more than one author it becomes a collaborative project
                        project_text = "Project Contributions: "
                        author_text = "Author: "
                        if len(author) >= 2:
                            project_text = "Collaborative Project Contributions: "
                            author_text = "Authors: "

                        # Add collaborative project details
                        pdf_output.multi_cell(
                            0,
                            10,
                            f"{author_text} {author} \n{project_text} {skills_text} \nCommit analysis: {commit_summary} \nKey skills demonstrated in this project: {project_skills_text}",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )
                        # TODO: Expand to include more details about the files in the git project

                    case "xlsx" | "xls" | "docx" | "odt" | "rtf":            
                        key_skills = []
                        summary = ""
                        extra_data_raw = file_analysis.extra_data

                        # Convert locally (do not mutate file_analysis.extra_data)
                        if isinstance(extra_data_raw, str):
                            try:
                                parsed = ast.literal_eval(extra_data_raw)
                                if isinstance(parsed, dict):
                                    key_skills = parsed.get("key_skills", []) or []
                                    summary = parsed.get("summary", "")
                            except (ValueError, SyntaxError):
                                # conversion failed: string isn't a valid Python literal dict
                                key_skills = []
                        elif isinstance(extra_data_raw, dict):
                            # In case it's already a dict for some reason, handle it too
                            key_skills = extra_data_raw.get("key_skills", []) or []
                            summary = extra_data_raw.get("summary", "")

                        # Final text to place in PDF
                        skills_text = ", ".join(key_skills) if key_skills else file_analysis.file_type.upper() + " Data Analysis"

                        pdf_output.multi_cell(
                            0,
                            10,
                            f"Key Skills demonstrated in this project: {skills_text}",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )
                        if file_analysis.file_type in ["docx", "odt", "rtf"]:
                            pdf_output.set_font(style="I")
                            pdf_output.multi_cell(
                                0,
                                10,
                                f"File Summary: {summary}",
                                new_x=XPos.LMARGIN,
                                new_y=YPos.NEXT,
                            )
                    # Add support for coding file extensions
                    case _ if ext in em:
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
                        skills_text = ", ".join(key_skills) if key_skills else extra_data_raw.get("language") + " Programming"

                        pdf_output.multi_cell(
                            0,
                            10,
                            f"Key Skills demonstrated in this project: {skills_text}",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )
                        pdf_output.multi_cell(
                            0,
                            10,
                            f"Code Complexity: {code_complexity}",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )

                    case "psd":
                        pdf_output.multi_cell(
                            0,
                            10,
                            f"Artistic Project: Photoshop Project",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )

                    case _:
                        # Add key skills for text files
                        pdf_output.multi_cell(
                            0,
                            10,
                            f"File type not analyzed. File details: {json.dumps(file_analysis.__dict__, indent=2)}",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )
                pdf_output.ln(10)  # Add a line break between entries
            # Save the PDF to disk
            pdf_output.output(str(export_path))
            return export_path
    except Exception as e:
        print(f"Something went wrong: {e}")

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


def generate_portfolio() -> Path | None:
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
    portfolio_export_resource_path: Path = portfolio_export_path_dir / ("resources")
    portfolio_export_resource_path.mkdir(parents=True, exist_ok=True)

    portfolio_export_path: Path = portfolio_export_path_dir / (
        todays_date + "-portfolio.html"
    )
    log_file: Path = Path(log.current_log_file)
    # Check if export directory exists
    if not portfolio_export_path_dir.exists():
        print(f"Export folder does not exist: {portfolio_export_path}")
        return
    try:
        with open(log_file, "r", encoding="utf-8") as lf:
            with open(portfolio_export_path, "w") as portfolio:
                # Write HTML header
                portfolio.write("<html><head><title>Portfolio</title></head><body>\n")
                portfolio.write("<h1>Project Portfolio</h1>\n")
                reader = csv.reader(lf)
                next(reader)  # Skip header row
                for row in reader:
                    file_analysis = FileAnalysis(*row)
                    # Copy file to resources folder with correct extension
                    file_analysis_source = Path(file_analysis.file_path)
                    if not file_analysis_source.is_dir():
                        shutil.copy(
                            file_analysis_source,
                            portfolio_export_resource_path
                            / (file_analysis.file_name + "." + file_analysis.file_type),
                        )
                    # Prepare details based on file type
                    # if file_analysis.file_type in image_types:
                    #     details = f"<p>Artistic Project:</p><img src='resources/{file_analysis.file_name}.{file_analysis.file_type}' alt='{file_analysis.file_name}' width='300'/>"
                    # elif file_analysis.file_type in collaborative_types:
                    #     details = (
                    #         f"<p>Project Contributions: {file_analysis.extra_data}</p>"
                    #     )
                    # else:
                    #     details = f"<p>Key Skills demonstrated in this project: {file_analysis.extra_data}</p>"

                    extra_dict = parse_extra_data(file_analysis.extra_data)
                    ext = file_analysis.file_type
                    details = ""
                    _, code_type = os.path.splitext(file_analysis.file_path)
                    code_type = code_type.lower()   
                    if ext in image_types:
                        img_meta = extra_dict.get("image", {})
                        img_format = img_meta.get("format", "Image")
                        width = img_meta.get("width")
                        height = img_meta.get("height")

                        project_desc = f"Digital Artwork ({img_format})"
                        if width and height:
                            project_desc += f" — {width} x {height}"

                        details = f"""
                            <p><strong>Artistic Project:</strong> {project_desc}</p>
                            <img src="resources/{file_analysis.file_name}.{ext}" width="300"/>
                        """
                    elif ext in collaborative_types:
                        details = f"""
                            <p><strong>Project Contributions:</strong></p>
                            <pre>{file_analysis.extra_data}</pre>
                        """
                    elif ext in ("xlsx", "xls", "docx", "odt", "rtf"):
                        key_skills = extra_dict.get("key_skills", [])
                        summary = extra_dict.get("summary", "")

                        skills_text = ", ".join(key_skills) if key_skills else f"{ext.upper()} Data Analysis"

                        details = f"""
                            <p><strong>Key Skills:</strong> {skills_text}</p>
                        """

                        if ext in ("docx", "odt", "rtf") and summary:
                            details += f"""
                                <p><em>File Summary:</em> {summary}</p>
                            """
                    elif code_type in em:
                        key_skills = extra_dict.get("key_skills", [])
                        complexity = extra_dict.get("complexity", {})
                        language = extra_dict.get("language", "Programming")

                        code_complexity = "Not Available"
                        if isinstance(complexity, dict):
                            code_complexity = complexity.get("estimated", "Not Available")

                        skills_text = ", ".join(key_skills) if key_skills else f"{language} Programming"

                        details = f"""
                            <p><strong>Key Skills:</strong> {skills_text}</p>
                            <p><em>Code Complexity:</em> {code_complexity}</p>
                        """
                    elif ext == "psd":
                        width = extra_dict.get("width")
                        height = extra_dict.get("height")
                        layers = extra_dict.get("number_of_layers")

                        psd_desc = "Photoshop Design Project"
                        if width and height:
                            psd_desc += f" — {width} x {height}"
                        if layers:
                            psd_desc += f" — {layers} Layers"

                        details = f"""
                            <p><strong>Artistic Project:</strong> {psd_desc}</p>
                        """

                    else:
                        details = f"""
                            <p><strong>File type not analyzed. File details: {json.dumps(file_analysis.__dict__, indent=2)}</p>
                        """


                    # Write entry to HTML
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
