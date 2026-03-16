import ast
import csv
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pandas.core.arrays.period import com
from typing_extensions import Any

import src.log.log as log
import src.param.param as param
from src.fas.fas import FileAnalysis
from src.log.log_sorter import LogSorter
from src.resume.resume_manager import manager
from utils.extension_mappings import CODING_FILE_EXTENSIONS as em

from src.showcase.showcase_portfolio_heatmap import ActivityHeatmap


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
        self.project_skills = []
        self.project_rank = 0
        self.include = True

    def add_file(self, file_analysis: FileAnalysis):
        if file_analysis.file_type == "Project":
            print(f"Processing project entry: {file_analysis.file_name}")
            self.valid_project_entry = True
            # Get valid dates for project duration
            if (
                isinstance(file_analysis.created_time, str)
                and file_analysis.created_time != "N/A"
                and file_analysis.created_time != ""
            ):
                try:
                    self.date_start = datetime.fromisoformat(file_analysis.created_time)
                except Exception as e:
                    pass
            if (
                isinstance(file_analysis.last_modified, str)
                and file_analysis.last_modified != "N/A"
                and file_analysis.last_modified != ""
            ):
                try:
                    self.date_end = datetime.fromisoformat(file_analysis.last_modified)
                except Exception as e:
                    pass

            self.title = file_analysis.file_name
            if isinstance(file_analysis.extra_data, dict):
                self.description = file_analysis.extra_data.get("description", "")

                # Get Manually set title
                new_title = file_analysis.extra_data.get("title", "")
                if new_title:
                    self.title = new_title

                # get manually set skills
                set_skills = file_analysis.extra_data.get("key_skills", [])
                if isinstance(set_skills, list):
                    for skill in set_skills:
                        if skill in self.skills:
                            self.skills[str(skill)] += 1
                        else:
                            self.skills[str(skill)] = 1

                # get manually set project_rank for project prioritization
                proj_importance = file_analysis.extra_data.get("project_rank", 0)
                if isinstance(proj_importance, (int, float)):
                    self.project_rank = float(proj_importance)

                # check if it should be included in the resume at all
                self.include = file_analysis.extra_data.get("include", True)
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
        if self.project_skills != []:
            return self.project_skills

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
        # Sort projects by rank (lowest first)
        sorted_projects = sorted(
            self.projects.items(), key=lambda item: item[1].project_rank, reverse=False
        )
        for key, project in sorted_projects:
            if self.project_counter >= self.project_limit:
                break
            self.project_counter += 1
            if project.include:
                yield self.projects.pop(key)
            else:
                self.projects.pop(key)

    def add_file_to_project(self, file_analysis: FileAnalysis) -> bool:
        if file_analysis.project_id is None:
            return False
        project_exists = file_analysis.project_id in self.projects
        if not project_exists:
            project = ShowcaseProject(file_analysis.project_id)
            self.projects[file_analysis.project_id] = project
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


def load_format_defaults(pdf: FPDF):
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Noto", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)


def end_section(pdf: FPDF, color=(0, 0, 0), thickness=0.5, spacing=4):
    # Set color and thickness
    pdf.ln(spacing)  # Add vertical space before the line
    pdf.set_draw_color(*color)
    pdf.set_line_width(thickness)
    y = pdf.get_y() + spacing  # Current y position + offset

    # Use page margins for line width
    left = pdf.l_margin
    right = pdf.w - pdf.r_margin

    pdf.line(left, y, right, y)
    pdf.ln(spacing + 2)  # Add vertical space after the line


def start_section(pdf: FPDF, color=(0, 0, 0), thickness=0.2, spacing=1):
    # Set color and thickness
    pdf.ln(spacing)  # Add vertical space before the line
    pdf.set_draw_color(*color)
    pdf.set_line_width(thickness)
    y = pdf.get_y() + spacing  # Current y position + offset

    # Use page margins for line width
    left = pdf.l_margin
    right = pdf.w - pdf.r_margin

    pdf.line(left, y, right, y)
    pdf.ln(spacing + 1)  # Add vertical space after the line


def create_resume_header(pdf: FPDF, personal_info: Dict[str, str]):
    load_format_defaults(pdf)
    name = personal_info.get("name", "")
    # write name title to pdf
    if name:
        pdf.set_font("Noto", "B", size=24)
        pdf.multi_cell(
            0, 8, clean_text(name), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )

    email = personal_info.get("email", "")
    phone_number = personal_info.get("phone_number", "")
    github = personal_info.get("github", "")
    linkedin = personal_info.get("linkedin", "")
    contact_items = []

    # Set formatting for contact info
    pdf.set_font("Noto", "B", size=10)

    if email:
        contact_items.append((email, None))
    if phone_number:
        contact_items.append((phone_number, None))
    if github:
        contact_items.append(("Github", github))
    if linkedin:
        contact_items.append(("LinkedIn", linkedin))
    if contact_items:
        item_widths = []
        for text, link in contact_items:
            item_widths.append(pdf.get_string_width(text) + 2)  # Add padding

        sep_width = pdf.get_string_width(" | ") if len(contact_items) > 1 else 0
        total_width = sum(item_widths) + sep_width * (len(contact_items) - 1)

        # Center the line
        page_width = pdf.w - 2 * pdf.l_margin
        start_x = pdf.l_margin + (page_width - total_width) / 2
        pdf.set_x(start_x)

        for i, (text, link) in enumerate(contact_items):
            if link:
                pdf.set_text_color(0, 0, 255)
            else:
                pdf.set_text_color(0, 0, 0)
            width = item_widths[i]
            pdf.cell(width, 6, text, ln=False, align="C", link=link)
            if i < len(contact_items) - 1:
                pdf.set_text_color(0, 0, 0)
                pdf.cell(sep_width, 6, " | ", ln=False, align="C")
        pdf.set_text_color(0, 0, 0)  #
    # end section if there is any header info to separate from the rest of the resume content
    if name or contact_items:
        end_section(pdf)


"""format for skill highlight list in param:
    { "skill": "", "include": false }
"""


def create_skill_highlight_section(pdf: FPDF, skill_highlight: List[Dict[str, str]]):
    load_format_defaults(pdf)
    if skill_highlight:
        skills = []
        for skill in skill_highlight:
            include = skill.get("include", True)
            skill = clean_text(skill.get("skill", ""))
            if include and skill:
                skills.append(skill)

        if not skills:
            return

        pdf.set_font("Noto", "B", size=18)
        pdf.multi_cell(0, 8, "Skills", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        start_section(pdf)
        pdf.set_font("Noto", size=12)
        for skill in skills:
            pdf.multi_cell(0, 5, "- " + skill, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        end_section(pdf)


"""
param format for education list in profile:
    {
        "title": "",
        "institution": "",
        "location": "",
        "completion_date": "",
        "description": "",
        "include": false
    }
"""


def create_education_section(pdf: FPDF, education: List[Dict[str, Any]]):
    load_format_defaults(pdf)
    if education:
        education_entries = []
        for edu in education:
            include = edu.get("include", True)
            if not include:
                continue
            education_entries.append(edu)
        if not education_entries:
            return
        pdf.set_font("Noto", "B", size=18)
        pdf.multi_cell(0, 8, "Education", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        start_section(pdf)
        pdf.set_font("Noto", size=12)
        for edu in education_entries:
            title = clean_text(edu.get("title", ""))
            institution = clean_text(edu.get("institution", ""))
            completion_date = clean_text(edu.get("completion_date", ""))
            description = clean_text(edu.get("description", ""))
            location = clean_text(edu.get("location", ""))

            header_line = f"{title}" if title else "Personal development"
            location_line = (
                f"{institution}, {location} - {completion_date}"
                if institution and location and completion_date
                else f"{institution}, {location}"
                if location
                else f"{institution}"
                if institution
                else ""
            )

            pdf.set_font("Noto", "B", size=14)
            pdf.multi_cell(0, 7, header_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if location_line:
                pdf.set_font("Noto", "I", size=10)
                pdf.multi_cell(0, 5, location_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if description:
                pdf.set_font("Noto", size=10)
                pdf.multi_cell(0, 5, description, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        end_section(pdf)


"""
param format for experience section in profile:
    {
        "company": "",
        "position": "",
        "location": "",
        "date_start": "",
        "date_end": "",
        "description": "",
        "responsibilities": [""],
        "include": false
    }
"""


def create_experience_section(pdf: FPDF, experience: List[Dict[str, Any]]):
    load_format_defaults(pdf)
    if experience:
        experience_entries = []
        for exp in experience:
            include = exp.get("include", True)
            if not include:
                continue
            experience_entries.append(exp)

        if not experience_entries:
            return

        pdf.set_font("Noto", "B", size=18)
        pdf.multi_cell(0, 8, "Experience", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        start_section(pdf)
        pdf.set_font("Noto", size=12)

        for exp in experience_entries:
            company = clean_text(exp.get("company", ""))
            position = clean_text(exp.get("position", ""))
            location = clean_text(exp.get("location", ""))
            date_start = clean_text(exp.get("date_start", ""))
            date_end = clean_text(exp.get("date_end", ""))
            description = clean_text(exp.get("description", ""))
            responsibilities = exp.get("responsibilities", [])
            if responsibilities and isinstance(responsibilities, list):
                responsibilities = [
                    clean_text(r) for r in responsibilities if clean_text(r)
                ]
            else:
                responsibilities = []

            header_line = (
                f"{position} at {company}"
                if position and company
                else company or position or "Work experience"
            )
            location_line = (
                f"{location} - {date_start} to {date_end}"
                if location and date_start and date_end
                else f"{location}"
                if location
                else f"{date_start} to {date_end}"
                if date_start and date_end
                else ""
            )

            pdf.set_font("Noto", "B", size=14)
            pdf.multi_cell(0, 7, header_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if location_line:
                pdf.set_font("Noto", "I", size=12)
                pdf.multi_cell(0, 5, location_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if description:
                pdf.set_font("Noto", size=12)
                pdf.multi_cell(0, 5, description, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if responsibilities:
                pdf.set_font("Noto", "I", size=11)
                for responsibility in responsibilities:
                    pdf.multi_cell(
                        0, 5, "- " + responsibility, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                    )
            pdf.ln(1)
        end_section(pdf)


# Template for resume entry in PDF
resume_entry_template = """{project_name}
{created_time} to {last_modified}
"""


def create_project_section(pdf_output: FPDF):
    load_format_defaults(pdf_output)
    project_manager: ShowcaseProjectManager = parse_project_entries()
    if not project_manager.projects:
        return
    # write section header
    pdf_output.set_font("Noto", "B", size=18)
    pdf_output.multi_cell(0, 8, "Projects", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    start_section(pdf_output)

    for project in project_manager.get_projects():
        entry = resume_entry_template.format(
            project_name=project.title,
            created_time=project.get_start_date(),
            last_modified=project.get_end_date(),
            project_description=project.description,
            project_skills="\n- ".join(project.get_skills()),
        )

        if project.title and isinstance(project.title, str):
            pdf_output.set_font("Noto", size=14, style="B")
            pdf_output.multi_cell(
                0, 8, project.title, new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
        else:
            pdf_output.set_font("Noto", size=14, style="B")
            pdf_output.multi_cell(
                0, 8, "Untitled Project", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )

        if (
            project.get_start_date()
            and project.get_end_date()
            and isinstance(project.get_start_date(), str)
            and isinstance(project.get_end_date(), str)
        ):
            pdf_output.set_font("Noto", size=12, style="I")
            pdf_output.multi_cell(
                0,
                6,
                f"{project.get_start_date()} to {project.get_end_date()}",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

        if project.description and isinstance(project.description, str):
            pdf_output.set_font("Noto", size=12)
            pdf_output.multi_cell(
                0, 6, project.description, new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
        skills = project.get_skills()
        if skills and isinstance(skills, list):
            pdf_output.set_font("Noto", size=11, style="I")
            for skill in skills:
                pdf_output.multi_cell(
                    0, 5, "- " + skill, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                )
        pdf_output.ln(1)
    end_section(pdf_output)


"""
Format for awards list in param:
    {
        "title": "",
        "issuer": "",
        "date": "",
        "description": "",
        "include": false
    }
"""


def create_awards_section(pdf_output: FPDF, awards_info: List[Dict[str, Any]]):
    load_format_defaults(pdf_output)
    if awards_info:
        awards_entries = []
        for award in awards_info:
            include = award.get("include", True)
            if not include:
                continue
            awards_entries.append(award)

        if not awards_entries:
            return

        pdf_output.set_font("Noto", "B", size=18)
        pdf_output.multi_cell(
            0, 8, "Awards & Certifications", new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        start_section(pdf_output)
        pdf_output.set_font("Noto", size=12)

        for award in awards_entries:
            title = clean_text(award.get("title", ""))
            issuer = clean_text(award.get("issuer", ""))
            date = clean_text(award.get("date", ""))
            description = clean_text(award.get("description", ""))

            header_line = (
                f"{title} from {issuer}"
                if title and issuer
                else title or issuer or "Award/Certification"
            )
            date_line = f"{date}" if date else ""

            pdf_output.set_font("Noto", "B", size=14)
            pdf_output.multi_cell(
                0, 7, header_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            if date_line:
                pdf_output.set_font("Noto", "I", size=12)
                pdf_output.multi_cell(
                    0, 5, date_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                )
            if description:
                pdf_output.set_font("Noto", size=12)
                pdf_output.multi_cell(
                    0, 5, description, new_x=XPos.LMARGIN, new_y=YPos.NEXT
                )
            pdf_output.ln(1)
        end_section(pdf_output)


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
    try:
        pdf_output = FPDF()
        pdf_output.add_page()
        pdf_output.add_font("Noto", "", "src/showcase/fonts/noto.ttf", uni=True)
        pdf_output.add_font("Noto", "B", "src/showcase/fonts/notob.ttf", uni=True)
        pdf_output.add_font("Noto", "I", "src/showcase/fonts/notoi.ttf", uni=True)
        pdf_output.add_font("Noto", "BI", "src/showcase/fonts/notobi.ttf", uni=True)

        pdf_output.set_font("Noto", "BI", size=14)

        # Write header

        personal_info = param.get("profile") or {}
        if not isinstance(personal_info, dict):
            print(
                "Warning: 'profile' parameter is not a dictionary. Skipping resume header generation."
            )
            personal_info = {}
        else:
            create_resume_header(pdf_output, personal_info)

        # Optional Skill highlight section

        skill_highlight = personal_info.get("highlighted_skills", [])
        if not isinstance(skill_highlight, list):
            print(
                "Warning: 'highlighted_skills' in profile is not a dictionary. Skipping skill highlight section."
            )
            skill_highlight = []
        else:
            create_skill_highlight_section(pdf_output, skill_highlight)

        # Education section

        education = personal_info.get("education", [])
        if not isinstance(education, list):
            print(
                "Warning: 'education' in profile is not a list. Skipping education section."
            )
        elif education:
            create_education_section(pdf_output, education)

        # work experience section

        experience = personal_info.get("work_experience", [])
        if not isinstance(experience, list):
            print(
                "Warning: 'work_experience' in profile is not a list. Skipping work experience section."
            )
        elif experience:
            create_experience_section(pdf_output, experience)

        # project section
        create_project_section(pdf_output)

        # awards section
        awards_info = personal_info.get("awards", [])
        if not isinstance(awards_info, list):
            print(
                "Warning: 'awards' in profile is not a list. Skipping awards section."
            )
        elif awards_info:
            create_awards_section(pdf_output, awards_info)

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
    
    # Fix: store projects in a list because get_projects() pops everything
    projects = list(project_manager.get_projects())
    
    heatmap = ActivityHeatmap()
    
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

            .heatmap-wrapper { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 30px; }
            .heatmap-days {
                display: grid;
                grid-template-rows: repeat(7, 15px);
                font-size: 10px;
                color: #555;
            }

            .heatmap-days div {
                display: flex;
                align-items: center;
            }
            .heatmap-months {
                display: grid;
                grid-auto-flow: column;
                grid-auto-columns: 15px;
                margin-bottom: 4px;
                font-size: 10px;
                color: #555;
                position: relative;
            }

            .month-label {
                text-align: left;
            }
            .heatmap-container {
                display: grid;
                grid-auto-flow: column;
                grid-template-rows: repeat(7, 12px);
                grid-auto-columns: 12px;
                gap: 3px;
            }
            .heatmap-day { width: 12px; height: 12px; border-radius: 2px; }
            .level-0 { background: #ebedf0; }
            .level-1 { background: #c6e48b; }
            .level-2 { background: #7bc96f; }
            .level-3 { background: #239a3b; }
            .level-4 { background: #196127; }
            .hidden { display: none !important; }

            .toggle-button { margin-bottom: 10px; padding: 6px 12px; font-size: 0.9em; cursor: pointer; border: none; border-radius: 6px; background: #2a3d66; color: #fff; }
            """
            (tmpdir_path / "style.css").write_text(css_content, encoding="utf-8")

            # Add all project activities to the heatmap BEFORE generating HTML
            for project in projects:
                heatmap.add_activity(project.get_start_date())
                heatmap.add_activity(project.get_end_date())

            # Generate heatmap HTML with labels
            heatmap_html = f"""
            <button class="toggle-button" onclick="document.querySelector('.heatmap-wrapper').classList.toggle('hidden')">Toggle Heatmap</button>
            <div class="heatmap-wrapper">
                <div class="heatmap-days">
                    <div></div><div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div>
                    <div>Thu</div><div>Fri</div><div>Sat</div>
                </div>
                <div>

                    {heatmap.generate_html()}
                </div>
            </div>
            """

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
                "<h2>Activity Heatmap</h2>",
                heatmap_html,
            ]

            for project in projects:
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

            html_parts.append("</div>")
            html_parts.append("<script>document.querySelector('.heatmap-wrapper').classList.remove('hidden');</script>")
            html_parts.append("</body></html>")

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
