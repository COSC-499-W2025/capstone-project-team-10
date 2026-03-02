from pathlib import Path
from typing import Optional, Dict, List

import src.log.log as log
import src.showcase.showcase as showcase
from src.fas.fas import FileAnalysis


class ResumeManager:
    """
    API-compliant ResumeManager.
    Uses ONLY log.py public functions.
    """

    def __init__(self, log_file: Optional[Path] = None):
        if log_file:
            log.current_log_file = str(log_file)

        self.log_file = Path(log.current_log_file)
        self.projects: Dict[str, FileAnalysis] = {}
        self.load_log()

    # ---------------------------------------------------
    # LOAD PROJECTS
    # ---------------------------------------------------

    def load_log(self):
        self.projects.clear()

        entries = log.get_project_entries()
        for fa in entries:
            if fa.file_type == "Project":
                self.projects[fa.project_id] = fa

    # ---------------------------------------------------
    # PROJECT INFO
    # ---------------------------------------------------

    def get_project_info(self, project_id: str) -> Optional[FileAnalysis]:
        return self.projects.get(project_id)

    def get_project_extra_attributes(self, project_id: str) -> dict:
        fa = self.get_project_info(project_id)
        if not fa:
            return {}
        if isinstance(fa.extra_data, dict):
            return fa.extra_data
        return {}

    # ---------------------------------------------------
    # PROJECT SKILLS
    # ---------------------------------------------------

    def get_project_skills(self, project_id: str) -> List[str]:
        skills = {}

        entries = log.get_project(project_id)
        for fa in entries:
            if isinstance(fa.extra_data, dict):
                file_skills = fa.extra_data.get("key_skills", [])
                if isinstance(file_skills, list):
                    for s in file_skills:
                        skills[s] = skills.get(s, 0) + 1

        # return sorted by frequency
        return sorted(skills.keys(), key=lambda x: skills[x], reverse=True)

    def set_project_skills(self, project_id: str, skills_csv: str):
        skills = [s.strip() for s in skills_csv.split(",") if s.strip()]

        entries = log.get_project(project_id)
        for fa in entries:
            if isinstance(fa.extra_data, dict):
                fa.extra_data["key_skills"] = skills
                log.update(fa, forceUpdate=True)

    # ---------------------------------------------------
    # PROJECT DESCRIPTION
    # ---------------------------------------------------

    def get_project_description(self, project_id: str) -> str:
        fa = self.get_project_info(project_id)
        if not fa:
            return ""

        if isinstance(fa.extra_data, dict):
            return fa.extra_data.get("description", "")

        return ""
    
    def set_project_description(self, project_id: str, description: str):
        fa = self.get_project_info(project_id)
        if not fa:
            return

        if not isinstance(fa.extra_data, dict):
            fa.extra_data = {}

        fa.extra_data["description"] = description
        log.update(fa, forceUpdate=True)
    # ---------------------------------------------------
    # RANK + SHOWCASE
    # ---------------------------------------------------

    def set_project_rank(self, project_id: str, rank: int):
        fa = self.get_project_info(project_id)
        if not fa:
            return

        if not isinstance(fa.extra_data, dict):
            fa.extra_data = {}

        fa.extra_data["project_rank"] = rank
        log.update(fa, forceUpdate=True)

    def set_showcase_flag(self, project_id: str, include: bool):
        fa = self.get_project_info(project_id)
        if not fa:
            return

        if not isinstance(fa.extra_data, dict):
            fa.extra_data = {}

        fa.extra_data["include"] = include
        log.update(fa, forceUpdate=True)

    # ---------------------------------------------------
    # RENAME PROJECT
    # ---------------------------------------------------

    def rename_project(self, project_id: str, new_name: str):
        entries = log.get_project(project_id)

        for fa in entries:
            if fa.file_type == "Project":
                fa.file_name = new_name
                log.update(fa, forceUpdate=True)

        self.load_log()

    # ------------------------------
    # DATE
    # ------------------------------
    def set_project_dates(self, project_id: str, start_date: str, end_date: str):
        """
        Save the start and end dates for a project in extra_data.
        Dates should be strings in yyyy-MM-dd format.
        """
        fa = self.get_project_info(project_id)
        if not fa:
            return

        if not isinstance(fa.extra_data, dict):
            fa.extra_data = {}

        fa.created_time = start_date
        fa.last_modified = end_date
        log.update(fa, forceUpdate=True)

    # ---------------------------------------------------
    # GENERATION
    # ---------------------------------------------------

    def get_full_resume_pdf(self, output_path: Optional[Path] = None):
        return showcase.generate_resume(output_file_path=output_path)

    def get_full_portfolio(self, output_path: Optional[Path] = None):
        return showcase.generate_portfolio(output_file_path=output_path)