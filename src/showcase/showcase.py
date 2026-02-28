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
from src.resume.resume_manager import manager
from utils.extension_mappings import CODING_FILE_EXTENSIONS as em


# Utils
class ShowcaseProject:
    def __init__(self, project_id: Optional[str] = None):
        self.skills: Dict[str, int] = {}
        self.valid_project_entry = False
        self.project_id = project_id
        self.title = project_id
        self.date_start = datetime.now()
        self.date_end = datetime.now()
        self.body = ""
        self.description = ""

    def add_file(self, file_analysis: FileAnalysis):
        if file_analysis.file_type == "Project":
            print(f"Processing project entry: {file_analysis.file_name}")
            self.valid_project_entry = True
            self.title = file_analysis.file_name
            if isinstance(file_analysis.extra_data, dict):
                self.description = file_analysis.extra_data.get("description", "")
                new_title = file_analysis.extra_data.get("title", "")
                if new_title:
                    self.title = new_title
        else:
            if not self.valid_project_entry:
                if self.date_start > datetime.fromisoformat(file_analysis.created_time):
                    self.date_start = datetime.fromisoformat(file_analysis.created_time)
                if self.date_end < datetime.fromisoformat(file_analysis.last_modified):
                    self.date_end = datetime.fromisoformat(file_analysis.last_modified)
            if isinstance(file_analysis.extra_data, dict):
                file_skills = file_analysis.extra_data.get("key_skills", [])
                if not isinstance(file_skills, list):
                    print(
                        f"Warning: 'skills' field in extra_data of file {file_analysis.file_name} is not a list. Skipping skill extraction for this file."
                    )
                    return
                for skill in file_skills:
                    if skill in self.skills:
                        self.skills[str(skill)] += 1
                    else:
                        self.skills[str(skill)] = 1

    def get_skills(self):
        # Create skills text based on file analyses
        max_skills = param.get("showcase.showcase_max_skills_per_project") or 10
        sorted_skills = [
            skill
            for skill, count in sorted(
                self.skills.items(), key=lambda item: item[1], reverse=True
            )
        ]
        if max_skills is not None:
            return sorted_skills[:max_skills]
        return sorted_skills

    def get_start_date(self):
        return self.date_start.strftime("%Y-%m-%d")

    def get_end_date(self):
        if self.date_end == "N/A":
            return "Current"
        now = datetime.now()
        one_month_ago = now - timedelta(days=30)
        if self.date_end > one_month_ago:
            return "Current"
        else:
            return self.date_end.strftime("%Y-%m-%d")


class ShowcaseProjectManager:
    def __init__(self):
        self.projects: Dict[str, ShowcaseProject] = {}
        self.project_limit = param.get("showcase.showcase_max_number_of_projects") or 10
        self.project_counter = 0

    def create_project(self, project_id: str) -> str:
        self.projects[project_id] = ShowcaseProject(project_id)
        return project_id

    def get_projects(self):
        while self.projects:
            first_key = next(iter(self.projects))
            yield self.projects.pop(first_key)

    def add_file_to_project(self, file_analysis: FileAnalysis) -> bool:
        if file_analysis.project_id is None:
            return False

        project_exists = file_analysis.project_id in self.projects

        if not project_exists and self.project_counter < self.project_limit:
            project = ShowcaseProject(file_analysis.project_id)
            self.projects[file_analysis.project_id] = project
            self.project_counter += 1
            self.projects[file_analysis.project_id].add_file(file_analysis)
            return True
        elif project_exists:
            self.projects[file_analysis.project_id].add_file(file_analysis)
            return True
        else:
            return False


def clean_text(text):
    text = " ".join(text.split())  # Remove extra spaces
    text = text.replace("\u00a0", " ")  # Replace non-breaking spaces
    return text


def parse_project_entries() -> ShowcaseProjectManager:
    project_manager = ShowcaseProjectManager()
    for line in log.follow_log(wait_for_new=False, return_file_analysis=True):
        if isinstance(line, FileAnalysis):
            project_manager.add_file_to_project(line)

    return project_manager


# Template for resume entry in PDF
resume_entry_template = """{project_name}
{created_time} to {last_modified}
{project_description}
Skills: {project_skills}
"""


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

    project_manager: ShowcaseProjectManager = parse_project_entries()

    try:
        pdf_output = FPDF()
        pdf_output.add_page()
        pdf_output.add_font("Noto", "", "src/showcase/fonts/noto.ttf", uni=True)
        pdf_output.add_font("Noto", "B", "src/showcase/fonts/notob.ttf", uni=True)
        pdf_output.add_font("Noto", "I", "src/showcase/fonts/notoi.ttf", uni=True)
        pdf_output.add_font("Noto", "BI", "src/showcase/fonts/notobi.ttf", uni=True)

        pdf_output.set_font("Noto", "BI", size=14)

        for project in project_manager.get_projects():
            entry = resume_entry_template.format(
                project_name=project.title,
                created_time=project.get_start_date(),
                last_modified=project.get_end_date(),
                project_description=project.description,
                project_skills=", ".join(project.get_skills()),
            )
            header_font_size = 18

            entry_lines = entry.splitlines()

            for i, line in enumerate(entry_lines):
                if i < 2:
                    pdf_output.set_font("Noto", size=header_font_size, style="B")
                    pdf_output.multi_cell(
                        0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                    )
                    header_font_size -= 2
                elif i == 2 and project.description != "":
                    print(f"Description: {project.description}")
                    pdf_output.set_font("Noto", size=14, style="I")
                    pdf_output.multi_cell(
                        0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                    )
                else:
                    pdf_output.set_font("Noto", size=12)
                    pdf_output.multi_cell(
                        0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                    )

            pdf_output.set_font("Noto", size=12)
            pdf_output.ln(10)
        pdf_output.output(str(export_path))

        try:
            # Store internally for the GUI history
            manager.create(
                export_path, {"type": "pdf_resume", "source_log": str(log_file)}
            )
        except Exception as e:
            print(f"Failed to store resume internally: {e}")
        return export_path
    except Exception as e:
        print(f"Something went wrong: {e}")


# Template for each portfolio entry in HTML
portfolio_entry_template = """
<div>
  <h2><a href={new_file_path}>{file_name}</a> - {file_type_upper}</h2>
  <h3>{created} to {modified}</h3>
  {details}
</div>
<hr/>
"""


def generate_portfolio(
    allow_image: bool = True, output_file_path: Optional[Path] = None
) -> Path | None:
    """
    Generates a web portfolio (HTML/CSS) from the log file and zips it.
    """
    import tempfile
    import zipfile
    from pathlib import Path

    todays_date: str = datetime.now().strftime("%m-%d-%y")
    export_zip_path: Path = Path(param.export_folder_path) / (
        todays_date + "-portfolio.zip"
    )
    file_number: int = 0
    if output_file_path is None:
        while export_zip_path.exists():
            file_number += 1
            export_zip_path = Path(param.export_folder_path) / (
                todays_date + f"-portfolio-{file_number}.zip"
            )
    if output_file_path is not None and isinstance(output_file_path, Path):
        export_zip_path = output_file_path

    log_file: Path = Path(log.current_log_file)
    if not export_zip_path.parent.exists():
        print(f"Export folder does not exist: {export_zip_path}")
        return

    project_manager: ShowcaseProjectManager = parse_project_entries()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            # Write CSS
            css_content = """
            body { font-family: Arial, sans-serif; background: #f8f8f8; margin: 0; padding: 0; }
            .container { max-width: 900px; margin: 40px auto; background: #fff; padding: 32px; border-radius: 12px; box-shadow: 0 2px 8px #0001; }
            .project { margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid #eee; }
            .project:last-child { border-bottom: none; }
            .project-title { font-size: 2em; font-weight: bold; color: #2a3d66; margin-bottom: 8px; }
            .project-dates { color: #888; margin-bottom: 8px; }
            .project-desc { margin-bottom: 8px; }
            .project-skills { color: #444; font-size: 1em; }
            """
            (tmpdir_path / "style.css").write_text(css_content, encoding="utf-8")

            # Write HTML
            html_parts = [
                "<!DOCTYPE html>",
                "<html lang='en'>",
                "<head>",
                "<meta charset='UTF-8'>",
                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
                "<title>My Project Portfolio</title>",
                "<link rel='stylesheet' href='style.css'>",
                "</head>",
                "<body>",
                "<div class='container'>",
                "<h1>My Project Portfolio</h1>",
            ]

            for project in project_manager.get_projects():
                html_parts.append("<div class='project'>")
                html_parts.append(f"<div class='project-title'>{project.title}</div>")
                html_parts.append(
                    f"<div class='project-dates'>{project.get_start_date()} to {project.get_end_date()}</div>"
                )
                html_parts.append(
                    f"<div class='project-desc'>{project.description or ''}</div>"
                )
                skills = ", ".join(project.get_skills())
                if skills:
                    html_parts.append(
                        f"<div class='project-skills'><b>Skills:</b> {skills}</div>"
                    )
                html_parts.append("</div>")

            html_parts.append("</div></body></html>")
            html_content = "\n".join(html_parts)
            (tmpdir_path / "index.html").write_text(html_content, encoding="utf-8")

            # Zip up the HTML and CSS
            with zipfile.ZipFile(export_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(tmpdir_path / "index.html", "index.html")
                zipf.write(tmpdir_path / "style.css", "style.css")

        try:
            # Store internally for the GUI history
            manager.create(
                export_zip_path, {"type": "web_portfolio", "source_log": str(log_file)}
            )
        except Exception as e:
            print(f"Failed to store portfolio internally: {e}")
        return export_zip_path
    except Exception as e:
        print(f"Something went wrong: {e}")


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
                    row.get("Customized", "").lower() == "true"
                    if row.get("Customized")
                    else False,
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
