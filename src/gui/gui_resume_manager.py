from pathlib import Path
import csv
from typing import Dict, Any, Optional
import src.log.log as log
import src.showcase.showcase as showcase
import ast

from src.fas.fas import FileAnalysis



class ResumeManager:
    """
    API-style manager for resume data.
    Provides project-level access and editing for the resume.
    """

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or Path(log.current_log_file)
        self.projects: Dict[str, FileAnalysis] = {}
        self.load_log()

    def load_log(self):
        """Load projects from the current log into memory."""
        self.projects.clear()
        if not self.log_file.exists():
            return
        with open(self.log_file, "r", encoding="utf-8") as lf:
            reader = csv.DictReader(lf)
            for row in reader:
                fa = FileAnalysis(
                    row.get("File path analyzed", ""),
                    row.get("File name", ""),
                    row.get("File type", ""),
                    row.get("Last modified", ""),
                    row.get("Created time", ""),
                    row.get("Extra data", ""),
                    row.get("Importance", ""),
                    row.get("Customized", ""),
                )
                self.projects[fa.file_name] = fa


    def get_project_info(self, project_name: str) -> Optional[FileAnalysis]:
        """Return the FileAnalysis for a single project."""
        return self.projects.get(project_name)

    def update_project_info(self, project_name: str, modifications: Dict[str, Any]):
        """
        Update a single project with modifications.
        Saves immediately to the log via log.update.
        """
        fa = self.projects.get(project_name)
        if not fa:
            return False

        # Apply modifications
        for key, value in modifications.items():
            if hasattr(fa, key):
                setattr(fa, key, value)

        # Persist to log
        log.update(fa, forceUpdate=True)
        # Refresh in-memory
        self.projects[project_name] = fa
        return True

    def get_full_resume_pdf(self, output_path: Optional[Path] = None) -> Path | None:
        """Generate full resume PDF from current projects."""
        # Ensure current log is up-to-date
        return showcase.generate_resume(output_file_path=output_path)
    
    def _parse_extra_data(self, extra_data_raw):
        if isinstance(extra_data_raw, dict):
            return extra_data_raw

        if isinstance(extra_data_raw, str):
            try:
                parsed = ast.literal_eval(extra_data_raw)
                if isinstance(parsed, dict):
                    return parsed
            except:
                pass

        return {}
    
    # Note that the CSV here is a simple comma-separated list of skills and not a full .CSV format
    def get_key_skills_csv(self, project_name: str) -> str:
        fa = self.projects.get(project_name)
        if not fa:
            return ""

        extra_dict = self._parse_extra_data(fa.extra_data)
        key_skills = extra_dict.get("key_skills", [])

        if isinstance(key_skills, list):
            return ", ".join([str(x).strip() for x in key_skills if str(x).strip()])

        # if it was stored weirdly
        if isinstance(key_skills, str):
            return key_skills.strip()

        return ""

    def set_key_skills_from_csv(self, project_name: str, skills_csv: str) -> bool:
        fa = self.projects.get(project_name)
        if not fa:
            return False

        extra_dict = self._parse_extra_data(fa.extra_data)

        # turn "Python, SQL, Git" -> ["Python", "SQL", "Git"]
        skills = [s.strip() for s in skills_csv.split(",") if s.strip()]

        extra_dict["key_skills"] = skills

        # store back as string (same format your log expects)
        fa.extra_data = str(extra_dict)

        log.update(fa, forceUpdate=True)
        self.projects[project_name] = fa
        return True
