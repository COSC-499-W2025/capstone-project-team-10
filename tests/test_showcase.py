import csv
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import src.showcase.showcase as showcase
from src.fas.fas import FileAnalysis

TEST_DIR = Path("test_output")
keep_files = False


def setup_test_dir():
    if TEST_DIR.exists() and not keep_files:
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_test_dir():
    if TEST_DIR.exists() and not keep_files:
        shutil.rmtree(TEST_DIR)


def make_file_analysis(
    file_name="file1",
    file_type="txt",
    file_path="testdata/test_showcase/file1.txt",
    last_modified="2023-01-02T00:00:00",
    created_time="2023-01-01T00:00:00",
    extra_data="skills",
):
    return FileAnalysis(
        file_name, file_type, file_path, last_modified, created_time, extra_data
    )


def test_format_last_modified_current():
    now = datetime.now().isoformat()
    fa = make_file_analysis(last_modified=now)
    assert showcase.format_last_modified(fa) == "Current"


def test_format_last_modified_old():
    old = (datetime.now() - timedelta(days=40)).isoformat()
    fa = make_file_analysis(last_modified=old)
    assert showcase.format_last_modified(fa) == datetime.fromisoformat(old).strftime(
        "%Y-%m-%d"
    )


def test_format_created_time():
    fa = make_file_analysis(created_time="2023-01-01T12:34:56")
    assert showcase.format_created_time(fa) == "2023-01-01"


def test_generate_resume():
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        # Write a test CSV row
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "tests/testdata/test_showcase/file1.txt",
                    "file1",
                    "txt",
                    "2023-01-02T00:00:00",
                    "2023-01-01T00:00:00",
                    "skills",
                ]
            )
            writer.writerow(
                [
                    "tests/testdata/test_showcase/bob.png",
                    "bob",
                    "jpg",
                    "2023-01-03T00:00:00",
                    "2023-01-01T00:00:00",
                    "artistic project",
                ],
            )
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
        cleanup_test_dir()


def test_generate_portfolio():
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        # Write a test CSV row
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "tests/testdata/test_showcase/file1.txt",
                    "file1",
                    "txt",
                    "2023-01-02T00:00:00",
                    "2023-01-01T00:00:00",
                    "skills",
                ],
            )
            # file_name, file_type, file_path, last_modified, created_time, extra_data
            writer.writerow(
                [
                    "tests/testdata/test_showcase/bob.png",
                    "bob",
                    "jpg",
                    "2023-01-03T00:00:00",
                    "2023-01-01T00:00:00",
                    "artistic project",
                ],
            )
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
        cleanup_test_dir()
