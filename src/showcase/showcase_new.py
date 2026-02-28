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
            self.valid_project_entry = True
            self.title = file_analysis.file_name
            if isinstance(file_analysis.extra_data, dict):
                self.description = file_analysis.extra_data.get("description", "")

        else:
            if not self.valid_project_entry:
                if self.date_start > datetime.fromisoformat(file_analysis.created_time):
                    self.date_start = datetime.fromisoformat(file_analysis.created_time)
                if self.date_end < datetime.fromisoformat(file_analysis.last_modified):
                    self.date_end = datetime.fromisoformat(file_analysis.last_modified)
            if isinstance(file_analysis.extra_data, dict):
                file_skills = file_analysis.extra_data.get("skills", [])
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

    def process_body(self):
        # Create body text based on file analyses
        body_lines = []


class ShowcaseProjectManager:
    def __init__(self):
        self.projects: Dict[str, ShowcaseProject] = {}
        self.project_limit = param.get("showcase.showcase_max_number_of_projects") or 10
        self.project_counter = 0

    def create_project(self, project_id: str) -> str:
        self.projects[project_id] = ShowcaseProject(project_id)
        return project_id

    def get_project(self) -> Optional[ShowcaseProject]:
        first_key = next(iter(self.projects))
        first_project = self.projects.pop(first_key)
        return first_project

    def add_file_to_project(self, file_analysis: FileAnalysis) -> bool:
        if file_analysis.project_id is None:
            return False
        if (
            self.projects[file_analysis.project_id] is None
            and self.project_counter < self.project_limit
        ):
            project = ShowcaseProject(file_analysis.project_id)
            self.projects[file_analysis.project_id] = project
            self.project_counter += 1
            self.projects[file_analysis.project_id].add_file(file_analysis)
            return True
        elif self.projects[file_analysis.project_id] is not None:
            self.projects[file_analysis.project_id].add_file(file_analysis)
            return True
        else:
            return False


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


def parse_project_entries() -> ShowcaseProjectManager:
    project_manager = ShowcaseProjectManager()
    for line in log.follow_log(wait_for_new=False, return_file_analysis=True):
        if isinstance(line, FileAnalysis):
            project_manager.add_file_to_project(line)

    return project_manager
