import csv
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pdfplumber
from bs4 import BeautifulSoup

import src.showcase.showcase as showcase
from src.fas.fas import FileAnalysis

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


def make_file_analysis(
    file_name="file1",
    file_type="txt",
    file_path="testdata/test_showcase/file1.txt",
    last_modified="2023-01-02T00:00:00",
    created_time="2023-01-01T00:00:00",
    extra_data="skills",
    importance=1.0,
    customized=False,
    project_id="",
):
    return FileAnalysis(
        file_path,
        file_name,
        file_type,
        last_modified,
        created_time,
        extra_data,
        importance,
        customized,
        project_id,
    )


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
