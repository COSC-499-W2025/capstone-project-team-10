import csv
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pdfplumber
import pytest
from bs4 import BeautifulSoup

import src.showcase.showcase as showcase
from src.fas.fas import FileAnalysis
from src.showcase.showcase import ShowcaseProject, ShowcaseProjectManager

resume_file_path = os.path.join("tests", "testdata", "test_showcase", "test_resume.pdf")
PDF_PATH = Path(resume_file_path)
portfolio_file_path = os.path.join(
    "tests", "testdata", "test_showcase", "test_portfolio.html"
)
PORTFOLIO_PATH = Path(portfolio_file_path)

TEST_DIR = Path("test_output")
keep_files = False


def setup_test_dir():
    if TEST_DIR.exists() and not keep_files:
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_test_dir():
    if TEST_DIR.exists() and not keep_files:
        shutil.rmtree(TEST_DIR)
    # Also clean up mock git directories
    git_test_dirs = [
        Path("tests/testdata/test_showcase/my_project"),
        Path("tests/testdata/test_showcase/team_project"),
    ]
    for git_dir in git_test_dirs:
        if git_dir.exists():
            shutil.rmtree(git_dir)


# Pass in a CSV Writer
def make_test_file(writer: Any) -> None:
    writer.writerow(
        [
            "File path analyzed",
            "File name",
            "File type",
            "Last modified",
            "Created time",
            "Extra data",
            "Importance",
            "Customized",
            "Project id",
        ]
    )
    writer.writerow(
        [
            "tests/testdata/test_showcase/file1.txt",
            "file1",
            "txt",
            "2023-01-02T00:00:00",
            "2023-01-01T00:00:00",
            "skills",
            "1.0",
            "False",
            "",
        ],
    )
    # file_path, file_name, file_type, last_modified, created_time, extra_data
    writer.writerow(
        [
            "tests/testdata/test_showcase/bob.png",
            "bob",
            "jpg",
            "2023-01-03T00:00:00",
            "2023-01-01T00:00:00",
            "artistic project",
            "2.0",
            "False",
            "",
        ],
    )


def make_test_file_with_git(writer: Any, create_git_dirs: bool = False) -> None:
    """Creates a test CSV file including git collaborative project entries

    Args:
        writer: CSV writer object
        create_git_dirs: If True, creates mock git project directories
    """
    make_test_file(writer)

    git_project_path_1 = "tests/testdata/test_showcase/my_project"
    git_project_path_2 = "tests/testdata/test_showcase/team_project"

    # Create mock git directories if requested
    if create_git_dirs:
        Path(git_project_path_1).mkdir(parents=True, exist_ok=True)
        Path(git_project_path_2).mkdir(parents=True, exist_ok=True)

    # Single author git project
    writer.writerow(
        [
            git_project_path_1,
            "my_project",
            "git",
            "2023-06-15T00:00:00",
            "2023-01-15T00:00:00",
            str(
                {
                    "key_skills": ["Python", "Git", "Version Control"],
                    "author": ["John Doe"],
                    "commits": {
                        "total_commits": 42,
                        "total_insertions": 1250,
                        "total_deletions": 380,
                        "net_change": 870,
                        "message_analysis": {
                            "feature implementation",
                            "bug fixes",
                            "documentation",
                        },
                    },
                    "extra data": [
                        {
                            "File name": "main.py",
                            "Extra data": {
                                "key_skills": ["Python", "API Development"],
                                "language": "Python",
                            },
                        },
                        {
                            "File name": "utils.py",
                            "Extra data": {
                                "key_skills": ["Python", "Data Processing"],
                                "language": "Python",
                            },
                        },
                    ],
                }
            ),
            "5.0",
            "False",
            "",
        ]
    )

    # Collaborative git project (multiple authors)
    writer.writerow(
        [
            git_project_path_2,
            "team_project",
            "git",
            "2023-08-20T00:00:00",
            "2023-03-10T00:00:00",
            str(
                {
                    "key_skills": [
                        "JavaScript",
                        "React",
                        "Node.js",
                        "Team Collaboration",
                    ],
                    "author": ["Alice Smith", "Bob Johnson", "Carol White"],
                    "commits": {
                        "total_commits": 156,
                        "total_insertions": 5420,
                        "total_deletions": 2100,
                        "net_change": 3320,
                        "message_analysis": {
                            "frontend development",
                            "backend API",
                            "testing",
                            "refactoring",
                        },
                    },
                    "extra data": [
                        {
                            "File name": "App.jsx",
                            "Extra data": {
                                "key_skills": ["React", "JavaScript", "UI Development"],
                                "language": "JavaScript",
                            },
                        },
                        {
                            "File name": "server.js",
                            "Extra data": {
                                "key_skills": ["Node.js", "Express", "API Design"],
                                "language": "JavaScript",
                            },
                        },
                        {
                            "File name": "tests.js",
                            "Extra data": {
                                "key_skills": ["Jest", "Testing", "JavaScript"],
                                "language": "JavaScript",
                            },
                        },
                    ],
                }
            ),
            "5.0",
            "False",
            "",
        ]
    )


def extract_pdf_text():
    """Return all text from the PDF"""
    text = ""
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_pdf_images():
    """Return a list of image objects in the PDF"""
    images = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            images.extend(page.images)
    return images


def load_portfolio_html():
    """Load portfolio HTML safely, ignoring binary content issues."""
    with open(PORTFOLIO_PATH, "rb") as f:  # open in binary mode
        content = f.read()
    text = content.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(text, "html.parser")
    return soup


def test_generate_resume():
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        # Write a test CSV row
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            make_test_file(writer)
        with (
            patch("src.showcase.showcase.param") as mock_param,
            patch("src.showcase.showcase.log") as mock_log,
        ):
            mock_param.export_folder_path = str(export_folder)
            mock_log.current_log_file = str(log_file)
            export_folder.mkdir(parents=True, exist_ok=True)
            showcase.generate_resume()
            # Now check for the PDF file
            pdf_files = list(export_folder.glob("*.pdf"))
            assert pdf_files, "No PDF file was created!"
    finally:
        print()
        cleanup_test_dir()


def test_generate_portfolio():
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        # Write a test CSV row
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            make_test_file(writer)
        with (
            patch("src.showcase.showcase.param") as mock_param,
            patch("src.showcase.showcase.log") as mock_log,
        ):
            mock_param.export_folder_path = str(export_folder)
            mock_log.current_log_file = str(log_file)
            showcase.generate_portfolio()
            # Find the portfolio export directory name
            todays_date = datetime.now().strftime("%m-%d-%y")
            expected_file = export_folder / f"{todays_date}-portfolio.zip"
            assert expected_file.exists(), "Portfolio zip export was not created!"
            # Extract the folder
            expected_dir = export_folder / f"{todays_date}-portfolio"
            import zipfile

            with zipfile.ZipFile(expected_file, "r") as zip_ref:
                zip_ref.extractall(expected_dir)

            # Check for the HTML file
            html_files = list(expected_dir.glob("*.html"))
            assert html_files, "No HTML portfolio file was created!"
            # Check that a zip file was created in the export folder
            zip_files = list(export_folder.glob("*.zip"))
            assert zip_files, "No zip archive was created in the test folder!"
    finally:
        print()
        cleanup_test_dir()


def test_generate_skill_timeline():
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        # Write a test CSV row
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            make_test_file(writer)
        with (
            patch("src.showcase.showcase.param") as mock_param,
            patch("src.showcase.showcase.log") as mock_log,
        ):
            mock_param.export_folder_path = str(export_folder)
            mock_log.current_log_file = str(log_file)
            export_folder.mkdir(parents=True, exist_ok=True)
            result_path = showcase.generate_skill_timeline()
            # Now check for the PDF file
            pdf_files = list(export_folder.glob("*.pdf"))
            assert pdf_files, "No skills timeline PDF file was created!"

            if result_path is not None:
                assert result_path.exists()
                assert result_path in pdf_files
    finally:
        print()
        cleanup_test_dir()


def test_showcase_project_add_file_and_skills():
    proj = showcase.ShowcaseProject("proj1")
    fa1 = FileAnalysis(
        "path",
        "file1",
        "txt",
        "2023-01-02T00:00:00",
        "2023-01-01T00:00:00",
        {"key_skills": ["Python", "Git"]},
        1.0,
        False,
        "proj1",
    )
    fa2 = FileAnalysis(
        "path",
        "file2",
        "txt",
        "2023-01-03T00:00:00",
        "2023-01-01T00:00:00",
        {"key_skills": ["Python", "API"]},
        1.0,
        False,
        "proj1",
    )
    proj.add_file(fa1)
    proj.add_file(fa2)
    skills = proj.get_skills()
    assert "Python" in skills
    assert "Git" in skills
    assert "API" in skills


def test_showcase_project_manager_add_and_get_projects():
    mgr = showcase.ShowcaseProjectManager()
    fa = FileAnalysis(
        "path",
        "file1",
        "txt",
        "2023-01-02T00:00:00",
        "2023-01-01T00:00:00",
        {"key_skills": ["Python"]},
        1.0,
        False,
        "proj1",
    )
    mgr.add_file_to_project(fa)
    projects = list(mgr.get_projects())
    assert len(projects) == 1
    assert projects[0].project_id == "proj1"


@pytest.fixture(autouse=True)
def patch_param(monkeypatch):
    param_mock = MagicMock()
    param_mock.get.side_effect = lambda key: {
        "showcase.showcase_max_skills_per_project": 3,
        "showcase.showcase_max_number_of_projects": 2,
    }.get(key, None)
    monkeypatch.setattr("src.showcase.showcase.param", param_mock)
    yield


def make_file_analysis(
    file_type="Other",
    file_name="file.txt",
    extra_data=None,
    created_time=None,
    last_modified=None,
    project_id=None,
):
    now = datetime.now()
    # Always convert to ISO string if not already a string
    created_time_str = (
        created_time.isoformat()
        if isinstance(created_time, datetime)
        else (created_time or now.isoformat())
    )
    last_modified_str = (
        last_modified.isoformat()
        if isinstance(last_modified, datetime)
        else (last_modified or now.isoformat())
    )
    return FileAnalysis(
        file_path="some/path",
        file_name=file_name,
        file_type=file_type,
        last_modified=last_modified_str,
        created_time=created_time_str,
        extra_data=extra_data,
        project_id=project_id,
    )


def test_add_file_project_entry_sets_fields():
    project = ShowcaseProject("proj1")
    file_analysis = make_file_analysis(
        file_type="Project",
        file_name="ProjectX",
        extra_data={
            "description": "A test project",
            "title": "Custom Title",
            "key_skills": ["Python", "SQL"],
            "project_rank": 5,
            "include": False,
        },
    )
    project.add_file(file_analysis)
    assert project.valid_project_entry
    assert project.title == "Custom Title"
    assert project.description == "A test project"
    assert project.skills == {"Python": 1, "SQL": 1}
    assert project.project_rank == 5
    assert not project.include


def test_add_file_non_project_entry_skill_aggregation():
    project = ShowcaseProject("proj2")
    file_analysis = make_file_analysis(
        file_type="Other",
        extra_data={"key_skills": ["Python", "Python", "C++"]},
        created_time=(datetime.now() - timedelta(days=10)).isoformat(),
        last_modified=(datetime.now() - timedelta(days=5)).isoformat(),
    )
    project.add_file(file_analysis)
    assert project.skills == {"Python": 2, "C++": 1}


def test_add_file_non_list_skills_warns_and_skips(capfd):
    project = ShowcaseProject("proj3")
    file_analysis = make_file_analysis(
        file_type="Other",
        extra_data={"key_skills": "notalist"},
    )
    project.add_file(file_analysis)
    out, _ = capfd.readouterr()
    assert "Warning" in out
    assert project.skills == {}


def test_get_skills_limits_and_sorts():
    project = ShowcaseProject("proj4")
    project.skills = {"Python": 5, "C++": 2, "Java": 3, "Go": 1}
    skills = project.get_skills()
    assert skills == ["Python", "Java", "C++"]  # Only top 3


def test_get_start_and_end_date():
    project = ShowcaseProject("proj5")
    now = datetime.now()
    project.date_start = now - timedelta(days=100)
    project.date_end = now - timedelta(days=40)
    assert project.get_start_date() == (now - timedelta(days=100)).strftime("%Y-%m-%d")
    assert project.get_end_date() == (now - timedelta(days=40)).strftime("%Y-%m-%d")


def test_get_end_date_current():
    project = ShowcaseProject("proj6")
    now = datetime.now()
    project.date_end = now
    assert project.get_end_date() == "Current"


def test_project_manager_create_and_add_file():
    mgr = ShowcaseProjectManager()
    pid = mgr.create_project("p1")
    assert pid == "p1"
    fa = make_file_analysis(project_id="p1", file_type="Project")
    assert mgr.add_file_to_project(fa)
    assert "p1" in mgr.projects


def test_project_manager_get_projects_limit_and_include():
    mgr = ShowcaseProjectManager()
    # Add 3 projects, only 2 should be yielded due to limit
    for i in range(3):
        pid = f"p{i}"
        mgr.create_project(pid)
        mgr.projects[pid].project_rank = i
        mgr.projects[pid].include = True
    projects = list(mgr.get_projects())
    assert len(projects) == 2
    assert all(isinstance(p, ShowcaseProject) for p in projects)


def test_project_entry_sets_dates():
    start = datetime(2020, 1, 1)
    end = datetime(2020, 12, 31)
    fa = make_file_analysis(
        file_type="Project",
        created_time=start,
        last_modified=end,
    )
    project = ShowcaseProject("proj1")
    project.add_file(fa)
    assert project.date_start == start
    assert project.date_end == end


def test_non_project_entry_updates_date_range():
    with patch("src.showcase.showcase.datetime") as mock_datetime:
        # Set the default now to a fixed date
        mock_datetime.now.return_value = datetime(2020, 1, 1)
        mock_datetime.fromisoformat.side_effect = lambda s: datetime.fromisoformat(s)
        project = ShowcaseProject("proj2")
        # Add a file with earlier created_time and later last_modified
        earlier = datetime(2019, 1, 1)
        later = datetime(2022, 1, 1)
        fa = make_file_analysis(
            file_type="Other",
            created_time=earlier,
            last_modified=later,
        )
        project.add_file(fa)
        assert project.date_start.date() == earlier.date()
        assert project.date_end.date() == later.date()


def test_non_project_entry_does_not_update_if_valid_project_entry():
    # Add a Project file first
    project = ShowcaseProject("proj3")
    project_start = datetime(2021, 5, 5)
    project_end = datetime(2021, 6, 6)
    fa_project = make_file_analysis(
        file_type="Project",
        created_time=project_start,
        last_modified=project_end,
    )
    project.add_file(fa_project)
    # Add a non-Project file with earlier/later dates
    earlier = datetime(2010, 1, 1)
    later = datetime(2030, 1, 1)
    fa_other = make_file_analysis(
        file_type="Other",
        created_time=earlier,
        last_modified=later,
    )
    project.add_file(fa_other)
    # Dates should not change after valid project entry
    assert project.date_start == project_start
    assert project.date_end == project_end


def make_ranked_file_analysis(
    project_id,
    project_rank,
    file_type="Project",
    file_name=None,
):
    now = datetime.now().isoformat()
    return FileAnalysis(
        file_path="some/path",
        file_name=file_name or f"Project_{project_id}",
        file_type=file_type,
        last_modified=now,
        created_time=now,
        extra_data={"project_rank": project_rank},
        project_id=project_id,
    )


def test_projects_are_sorted_by_rank():
    mgr = ShowcaseProjectManager()
    mgr.project_limit = 99  # Ensure all projects are yielded
    projects = [
        ("A", 5),
        ("B", 1),
        ("C", 3),
        ("D", 2),
        ("E", 4),
    ]
    for pid, rank in projects:
        fa = make_ranked_file_analysis(pid, rank)
        mgr.add_file_to_project(fa)
    yielded = [p.project_id for p in mgr.get_projects()]
    assert yielded == ["B", "D", "C", "E", "A"]


def test_projects_with_same_rank_keep_insertion_order():
    mgr = ShowcaseProjectManager()
    mgr.project_limit = 99  # Ensure all projects are yielded
    for pid in ["X", "Y", "Z"]:
        fa = make_ranked_file_analysis(pid, 0)
        mgr.add_file_to_project(fa)
    yielded = [p.project_id for p in mgr.get_projects()]
    assert yielded == ["X", "Y", "Z"]


def test_project_skills_override():
    project = ShowcaseProject("proj_override")
    # Add a file with some skills
    fa = FileAnalysis(
        file_path="some/path",
        file_name="file1",
        file_type="Project",
        last_modified=datetime.now().isoformat(),
        created_time=datetime.now().isoformat(),
        extra_data={"key_skills": ["Python", "SQL"]},
        project_id="proj_override",
    )
    project.add_file(fa)
    # By default, get_skills returns the computed skills
    computed_skills = project.get_skills()
    assert set(computed_skills) == {"Python", "SQL"}

    # Now override with project_skills
    project.project_skills = ["CustomSkill1", "CustomSkill2"]
    overridden_skills = project.get_skills()
    assert overridden_skills == ["CustomSkill1", "CustomSkill2"]
