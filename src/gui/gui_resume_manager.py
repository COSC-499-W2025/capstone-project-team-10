from pathlib import Path
import csv
from typing import Dict, Any, Optional, List
import json
import src.log.log as log
import src.showcase.showcase as showcase

from src.fas.fas import FileAnalysis


class ResumeManager:
    """
    API-style manager for resume data.
    Only exposes FileType == "Project"
    Aggregates skills from files under same Project id.
    """

    def __init__(self, log_file: Optional[Path] = None):
        if log_file:
            self.log_file = log_file
        else:
            self.log_file = Path(log.current_log_file)

        # Only project-level entries
        self.projects: Dict[str, FileAnalysis] = {}

        # All log rows (needed for aggregation)
        self.all_rows: List[dict] = []

        self.load_log()

    # ---------------------------------------------------
    # LOAD
    # ---------------------------------------------------
    def load_log(self):
        self.projects.clear()
        self.all_rows.clear()

        if not self.log_file.exists():
            return

        with open(self.log_file, "r", encoding="utf-8") as lf:
            reader = csv.DictReader(lf)

            for row in reader:
                self.all_rows.append(row)

                # ONLY store rows that are actual Projects
                if row.get("File type") == "Project":
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

    # ---------------------------------------------------
    # PROJECT ACCESS
    # ---------------------------------------------------
    def get_project_info(self, project_name: str) -> Optional[FileAnalysis]:
        return self.projects.get(project_name)

    # ---------------------------------------------------
    # SKILL AGGREGATION
    # ---------------------------------------------------
    def _parse_extra_data(self, raw):
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except:
            return {}

    def get_project_skills(self, project_name: str) -> List[str]:
        """
        Collect all key_skills from files under same Project id.
        """
        project = self.projects.get(project_name)
        if not project:
            return []

        project_id = project.file_name  # matches "Project id" column

        collected = set()

        for row in self.all_rows:
            if row.get("Project id") != project_id:
                continue

            if row.get("File type") == "Project":
                continue  # skip the parent row

            extra = self._parse_extra_data(row.get("Extra data"))
            skills = extra.get("key_skills", [])

            if isinstance(skills, list):
                for s in skills:
                    if s:
                        collected.add(s.strip())

        return sorted(collected)

    def set_project_skills(self, project_name: str, skills_csv: str):
        """
        Overwrites key_skills for all files under this project.
        """
        project = self.projects.get(project_name)
        if not project:
            return False

        project_id = project.file_name
        new_skills = [s.strip() for s in skills_csv.split(",") if s.strip()]

        for row in self.all_rows:
            if row.get("Project id") != project_id:
                continue

            if row.get("File type") == "Project":
                continue

            extra = self._parse_extra_data(row.get("Extra data"))
            extra["key_skills"] = new_skills
            row["Extra data"] = json.dumps(extra)

        # Rewrite entire CSV safely
        self._rewrite_log()
        self.load_log()
        return True

    def _rewrite_log(self):
        if not self.all_rows:
            return

        fieldnames = self.all_rows[0].keys()

        with open(self.log_file, "w", encoding="utf-8", newline="") as lf:
            writer = csv.DictWriter(lf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.all_rows)

    # ---------------------------------------------------
    # PDF
    # ---------------------------------------------------
    def get_full_resume_pdf(self, output_path: Optional[Path] = None):
        original_log = log.current_log_file

        try:
            # Start from the log file chosen by the user
            log.current_log_file = str(self.log_file)

            # Check if any projects are marked for showcase
            showcase_projects = [
                p.file_name
                for p in self.projects.values()
                if self.get_project_extra_attributes(p.file_name).get("showcase", False)
            ]

            # If none are checked, fallback to full resume
            if not showcase_projects:
                return showcase.generate_resume(output_file_path=output_path)

            # Otherwise, create a temp CSV containing only showcase projects
            import tempfile, csv

            with tempfile.NamedTemporaryFile("w+", delete=False, newline="", suffix=".log") as tmpfile:
                writer = csv.DictWriter(tmpfile, fieldnames=self.all_rows[0].keys())
                writer.writeheader()
                for row in self.all_rows:
                    # Include parent Project row only if in showcase_projects
                    if row.get("File type") == "Project" and row.get("File name") not in showcase_projects:
                        continue

                    # Include child rows only if parent is in showcase_projects
                    project_id = row.get("Project id")
                    if project_id and project_id not in showcase_projects:
                        continue

                    writer.writerow(row)

                tmpfile.flush()
                log.current_log_file = tmpfile.name
                return showcase.generate_resume(output_file_path=output_path)
        finally:
            # Restore original log (user-chosen one)
            log.current_log_file = str(self.log_file)

    def get_full_portfolio(self, output_path: Optional[Path] = None):
        original_log = log.current_log_file

        try:
            log.current_log_file = str(self.log_file)

            # Only include projects marked for showcase
            showcase_projects = [
                p.file_name
                for p in self.projects.values()
                if self.get_project_extra_attributes(p.file_name).get("showcase", False)
            ]

            # If none are checked, fallback to full portfolio
            if not showcase_projects:
                return showcase.generate_portfolio(output_file_path=output_path)

            # Otherwise, create a temp CSV containing only showcase projects
            import tempfile, csv

            with tempfile.NamedTemporaryFile("w+", delete=False, newline="", suffix=".log") as tmpfile:
                writer = csv.DictWriter(tmpfile, fieldnames=self.all_rows[0].keys())
                writer.writeheader()
                for row in self.all_rows:
                    # Include parent Project row only if in showcase_projects
                    if row.get("File type") == "Project" and row.get("File name") not in showcase_projects:
                        continue

                    # Include child rows only if parent is in showcase_projects
                    project_id = row.get("Project id")
                    if project_id and project_id not in showcase_projects:
                        continue

                    writer.writerow(row)

                tmpfile.flush()
                log.current_log_file = tmpfile.name
                return showcase.generate_portfolio(output_file_path=output_path)
        finally:
            log.current_log_file = str(self.log_file)
    
    def set_project_rank(self, project_name: str, rank: int):
        """Set display rank for project."""
        project = self.projects.get(project_name)
        if not project:
            return False
        extra = self._parse_extra_data(project.extra_data)
        extra["rank"] = rank
        project.extra_data = json.dumps(extra)
        self._update_row_extra_data(project_name, extra)
        return True

    def set_showcase_flag(self, project_name: str, showcase: bool):
        project = self.projects.get(project_name)
        if not project:
            return False
        extra = self._parse_extra_data(project.extra_data)
        extra["showcase"] = showcase
        project.extra_data = json.dumps(extra)
        self._update_row_extra_data(project_name, extra)
        return True

    def set_highlighted_skills(self, project_name: str, skills: List[str]):
        project = self.projects.get(project_name)
        if not project:
            return False
        extra = self._parse_extra_data(project.extra_data)
        extra["highlighted_skills"] = skills
        project.extra_data = json.dumps(extra)
        self._update_row_extra_data(project_name, extra)
        return True

    def _update_row_extra_data(self, project_name: str, extra: dict):
        """Helper to rewrite extra data in all rows under project."""
        project = self.projects.get(project_name)
        if not project:
            return
        project_id = project.file_name
        for row in self.all_rows:
            if row.get("Project id") != project_id:
                continue
            row_extra = self._parse_extra_data(row.get("Extra data"))
            row_extra.update(extra)
            row["Extra data"] = json.dumps(row_extra)
        self._rewrite_log()
        self.load_log()

    def get_project_extra_attributes(self, project_name: str) -> dict:
        """Return rank, showcase, highlighted_skills, importance, customized, etc."""
        project = self.projects.get(project_name)
        if not project:
            return {}
        extra = self._parse_extra_data(project.extra_data)
        return {
            "rank": extra.get("rank", 0),
            "showcase": extra.get("showcase", False),
            "highlighted_skills": extra.get("highlighted_skills", []),
            "importance": project.importance,
            "customized": project.customized
        }
    
    def rename_project(self, old_name: str, new_name: str):
        """Rename a project and all its child rows in the log."""
        if old_name not in self.projects:
            return False

        # Update the dictionary key
        self.projects[new_name] = self.projects.pop(old_name)

        # Update the FileAnalysis object
        self.projects[new_name].file_name = new_name

        # Update all rows in the log
        for row in self.all_rows:
            if row.get("Project id") == old_name:
                row["Project id"] = new_name  # children reference new project_id
            if row.get("File type") == "Project" and row.get("File name") == old_name:
                row["File name"] = new_name

        self._rewrite_log()
        self.load_log()
        return True