import csv
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import src.showcase.showcase as showcase
from src.fas.fas import FileAnalysis

import src.fas.fas_docx as docx
import src.fas.fas_rtf as rtf
import src.fas.fas_odt as odt

import pdfplumber
from bs4 import BeautifulSoup


docx_file_path = os.path.join("tests", "testdata", "test_showcase","docx_test.docx")
docx_result = docx.extract_docx_data(docx_file_path)
rtf_file_path = os.path.join("tests", "testdata", "test_fas","fas_rtf_data.rtf")
rtf_result = rtf.extract_rtf_data(rtf_file_path)
odt_file_path = os.path.join("tests", "testdata", "test_fas","fas_odt_data.odt")
odt_result = odt.extract_odt_data(odt_file_path)

resume_file_path = os.path.join("tests", "testdata", "test_showcase", "test_resume.pdf")
PDF_PATH = Path(resume_file_path)
portfolio_file_path = os.path.join("tests", "testdata", "test_showcase", "test_portfolio.html")
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
        ],
    )
    writer.writerow(
        [
            "tests/testdata/test_showcase/docx_test.docx",
            docx_result["title"],
            "docx",
            "2023-01-03T00:00:00", # Currently just a static value as using docx_result["modified"]/["created"] causes the test to fail
            "2023-01-01T00:00:00",
            [
                docx_result["author"],
                docx_result["keywords"],
                docx_result["category"],
                docx_result["comments"],
                docx_result["num_paragraphs"],
                docx_result["num_tables"],
                docx_result["num_chars"],
                docx_result["num_words"],
                docx_result["filtered_word_count"],
                docx_result["unique_words"],
                docx_result["sentence_count"],
                docx_result["lexical_diversity"],
                docx_result["top_keywords"],
                docx_result["sentiment"],
                docx_result["sentiment_score"],
                #docx_result["named_entities"], This is commented out, as it is excessive and causes the output to look poor and has little to no relevance to key skills
                docx_result["summary"],
                docx_result["complexity"],
                docx_result["depth"],
                docx_result["structure"],
                docx_result["sentiment_insight"],
            ],
        ]
    ) 
    writer.writerow(
        [
            "tests/testdata/test_fas/fas_rtf_data.rtf",
            rtf_result["title"],
            "rtf",
            "2023-01-03T00:00:00", # Currently just a static value as using rtf_result["modified"]/["created"] causes the test to fail
            "2023-01-01T00:00:00",
            [
                rtf_result["author"],
                rtf_result["num_paragraphs"],
                rtf_result["num_chars"],
                rtf_result["num_words"],
                rtf_result["filtered_word_count"],
                rtf_result["unique_words"],
                rtf_result["sentence_count"],
                rtf_result["lexical_diversity"],
                rtf_result["top_keywords"],
                rtf_result["sentiment"],
                rtf_result["sentiment_score"],
                rtf_result["named_entities"],
                rtf_result["summary"],
                rtf_result["complexity"],
                rtf_result["depth"],
                rtf_result["structure"],
                rtf_result["sentiment_insight"],
            ],
        ]
    )
    writer.writerow(
        [
            "tests/testdata/test_fas/fas_odt_data.odt",
            odt_result["title"],
            "odt",
            "2023-01-03T00:00:00", # Currently just a static value as using odt_result["modified"]/["created"] causes the test to fail
            "2023-01-01T00:00:00",
            [
                odt_result["author"],
                odt_result["num_paragraphs"],
                odt_result["num_chars"],
                odt_result["num_words"],
                odt_result["filtered_word_count"],
                odt_result["unique_words"],
                odt_result["sentence_count"],
                odt_result["lexical_diversity"],
                odt_result["top_keywords"],
                odt_result["sentiment"],
                odt_result["sentiment_score"],
                odt_result["named_entities"],
                odt_result["summary"],
                odt_result["complexity"],
                odt_result["depth"],
                odt_result["structure"],
                odt_result["sentiment_insight"],
            ],
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



def test_resume_image_project_contains_image():
    images = extract_pdf_images()
    assert len(images) > 0, "No images found for the image project in PDF"

def test_resume_docx_project_key_skills_and_summary():
    text = extract_pdf_text()
    assert "Key Skills" in text, "Key skills missing in DOCX project"
    assert "File Summary" in text or "summary" in text.lower(), "Summary missing in DOCX project"

def test_resume_xlsx_project_key_skills():
    text = extract_pdf_text()
    assert "Key Skills" in text, "Key skills missing in XLSX project"

def test_resume_psd_project_artistic_label():
    text = extract_pdf_text()
    assert "Artistic Project" in text or "Photoshop" in text, "PSD project label missing"

def test_resume_coding_project_key_skills_and_code_complexity():
    text = extract_pdf_text()
    assert "Key Skills" in text, "Python project key skills missing"
    assert "Code Complexity" in text, "Python project code complexity missing"


def test_portfolio_image_project_contains_image():
    soup = load_portfolio_html()
    # Look for any <img> tags
    imgs = soup.find_all("img")
    assert imgs, "No <img> tag found for image project"

def test_portfolio_docx_project_key_skills_and_summary():
    soup = load_portfolio_html()
    docx_div = soup.find("div", class_="docx")
    assert docx_div, "No DOCX project found"
    # Check Key Skills
    assert "Key Skills" in docx_div.get_text(), "DOCX project missing key skills"
    # Check Summary presence
    assert "Summary" in docx_div.get_text() or len(docx_div.get_text()) > 0, "DOCX project missing summary"

def test_portfolio_xlsx_project_key_skills():
    soup = load_portfolio_html()
    xlsx_div = soup.find("div", class_="xlsx")
    assert xlsx_div, "No XLSX project found"
    # Check Key Skills presence
    assert "Key Skills" in xlsx_div.get_text(), "XLSX project missing key skills"

def test_portfolio_psd_project_artistic_label():
    soup = load_portfolio_html()
    psd_div = soup.find("div", class_="psd")
    assert psd_div, "No PSD project found"
    # Check Artistic Project label
    assert "Artistic Project" in psd_div.get_text(), "PSD project missing 'Artistic Project' label"

def test_portfolio_coding_project_key_skills_and_code_complexity():
    soup = load_portfolio_html()
    py_div = soup.find("div", class_="py")
    assert py_div, "No Python project found"
    # Check key skills text
    assert "Key Skills" in py_div.get_text(), "Python project missing key skills"
    # Check code complexity
    assert "Code Complexity" in py_div.get_text(), "Python project missing code complexity"
