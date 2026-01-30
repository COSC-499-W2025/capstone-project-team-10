from pathlib import Path
import csv
from typing import Dict, Any, Optional
import src.log.log as log
import src.showcase.showcase as showcase
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
