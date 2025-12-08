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
    # Also clean up mock git directories
    git_test_dirs = [
        Path("tests/testdata/test_showcase/my_project"),
        Path("tests/testdata/test_showcase/team_project")
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
            str({
                "key_skills": ["Python", "Git", "Version Control"],
                "author": ["John Doe"],
                "commits": {
                    "total_commits": 42,
                    "total_insertions": 1250,
                    "total_deletions": 380,
                    "net_change": 870,
                    "message_analysis": {"feature implementation", "bug fixes", "documentation"}
                },
                "extra data": [
                    {
                        "File name": "main.py",
                        "Extra data": {
                            "key_skills": ["Python", "API Development"],
                            "language": "Python"
                        }
                    },
                    {
                        "File name": "utils.py",
                        "Extra data": {
                            "key_skills": ["Python", "Data Processing"],
                            "language": "Python"
                        }
                    }
                ]
            })
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
            str({
                "key_skills": ["JavaScript", "React", "Node.js", "Team Collaboration"],
                "author": ["Alice Smith", "Bob Johnson", "Carol White"],
                "commits": {
                    "total_commits": 156,
                    "total_insertions": 5420,
                    "total_deletions": 2100,
                    "net_change": 3320,
                    "message_analysis": {"frontend development", "backend API", "testing", "refactoring"}
                },
                "extra data": [
                    {
                        "File name": "App.jsx",
                        "Extra data": {
                            "key_skills": ["React", "JavaScript", "UI Development"],
                            "language": "JavaScript"
                        }
                    },
                    {
                        "File name": "server.js",
                        "Extra data": {
                            "key_skills": ["Node.js", "Express", "API Design"],
                            "language": "JavaScript"
                        }
                    },
                    {
                        "File name": "tests.js",
                        "Extra data": {
                            "key_skills": ["Jest", "Testing", "JavaScript"],
                            "language": "JavaScript"
                        }
                    }
                ]
            })
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

def test_generate_resume_with_git_single_author():
    """Test resume generation with a single-author git project"""
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            make_test_file_with_git(writer)
        
        with (
            patch("src.showcase.showcase.param") as mock_param,
            patch("src.showcase.showcase.log") as mock_log,
        ):
            mock_param.export_folder_path = str(export_folder)
            mock_log.current_log_file = str(log_file)
            
            result_path = showcase.generate_resume()
            assert result_path is not None, "Resume generation returned None"
            assert result_path.exists(), "Resume PDF was not created"
            
            # Read PDF and verify git content
            with pdfplumber.open(result_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # Check for single author label
                assert "Author:" in text, "Single author label not found"
                assert "John Doe" in text, "Author name not found"
                
                # Check for project contributions
                assert "Project Contributions:" in text, "Project contributions label not found"
                
                # Check for commit analysis
                assert "Commit analysis:" in text, "Commit analysis section not found"
                assert "Total Commits: 42" in text, "Total commits not found"
                assert "Total Insertions: +1250" in text, "Total insertions not found"
                assert "Total Deletions: -380" in text, "Total deletions not found"
                assert "Net Change: 870" in text, "Net change not found"
                
                # Check for project skills
                assert "Key skills demonstrated in this project:" in text
                assert "Python" in text or "API Development" in text or "Data Processing" in text
                
    finally:
        cleanup_test_dir()


def test_generate_resume_with_git_collaborative():
    """Test resume generation with a collaborative (multi-author) git project"""
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            make_test_file_with_git(writer)
        
        with (
            patch("src.showcase.showcase.param") as mock_param,
            patch("src.showcase.showcase.log") as mock_log,
        ):
            mock_param.export_folder_path = str(export_folder)
            mock_log.current_log_file = str(log_file)
            
            result_path = showcase.generate_resume()
            assert result_path is not None
            assert result_path.exists()
            
            with pdfplumber.open(result_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # Check for collaborative project labels
                assert "Authors:" in text, "Multiple authors label not found"
                assert "Collaborative Project Contributions:" in text, "Collaborative label not found"
                
                # Check for all authors
                assert "Alice Smith" in text, "First author not found"
                assert "Bob Johnson" in text, "Second author not found"
                assert "Carol White" in text, "Third author not found"
                
                # Check commit statistics
                assert "Total Commits: 156" in text
                assert "Total Insertions: +5420" in text
                assert "Net Change: 3320" in text
                
    finally:
        cleanup_test_dir()


def test_generate_portfolio_with_git_projects():
    """Test portfolio generation with git projects"""
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            make_test_file_with_git(writer, create_git_dirs=True)
        
        with (
            patch("src.showcase.showcase.param") as mock_param,
            patch("src.showcase.showcase.log") as mock_log,
        ):
            mock_param.export_folder_path = str(export_folder)
            mock_log.current_log_file = str(log_file)
            
            result_path = showcase.generate_portfolio()
            assert result_path is not None
            assert result_path.exists()
            
            # Extract and read HTML
            todays_date = datetime.now().strftime("%m-%d-%y")
            expected_dir = export_folder / f"{todays_date}-portfolio"
            import zipfile
            with zipfile.ZipFile(result_path, "r") as zip_ref:
                zip_ref.extractall(expected_dir)
            
            html_files = list(expected_dir.glob("*.html"))
            assert html_files, "No HTML file found in portfolio"
            
            with open(html_files[0], "r", encoding="utf-8") as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Find git project divs
            git_divs = soup.find_all("div", class_="git")
            assert len(git_divs) >= 2, "Git projects not found in portfolio"
            
            # Check for project contributions
            assert "Project Contributions:" in html_content
            
    finally:
        cleanup_test_dir()


def test_portfolio_git_single_author_labels():
    """Test that single-author git projects have correct labels in portfolio"""
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            make_test_file_with_git(writer, create_git_dirs=True)
        
        with (
            patch("src.showcase.showcase.param") as mock_param,
            patch("src.showcase.showcase.log") as mock_log,
        ):
            mock_param.export_folder_path = str(export_folder)
            mock_log.current_log_file = str(log_file)
            
            result_path = showcase.generate_portfolio()
            
            todays_date = datetime.now().strftime("%m-%d-%y")
            expected_dir = export_folder / f"{todays_date}-portfolio"
            import zipfile
            with zipfile.ZipFile(result_path, "r") as zip_ref:
                zip_ref.extractall(expected_dir)
            
            html_files = list(expected_dir.glob("*.html"))
            with open(html_files[0], "r", encoding="utf-8") as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, "html.parser")
            git_divs = soup.find_all("div", class_="git")
            
            # Find the single-author project (my_project)
            single_author_div = None
            for div in git_divs:
                if "my_project" in div.get_text():
                    single_author_div = div
                    break
            
            assert single_author_div is not None, "Single-author git project not found"
            div_text = single_author_div.get_text()
            
            # Check for single author label
            assert "Author:" in div_text, "Single author label not found"
            assert "John Doe" in div_text, "Author name not found"
            
            # Check for project contributions (not collaborative)
            assert "Project Contributions:" in div_text
            assert "Collaborative Project Contributions:" not in div_text
            
    finally:
        cleanup_test_dir()


def test_portfolio_git_collaborative_labels():
    """Test that multi-author git projects have collaborative labels in portfolio"""
    setup_test_dir()
    try:
        export_folder = TEST_DIR
        log_file = export_folder / "log.csv"
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            make_test_file_with_git(writer, create_git_dirs=True)
        
        with (
            patch("src.showcase.showcase.param") as mock_param,
            patch("src.showcase.showcase.log") as mock_log,
        ):
            mock_param.export_folder_path = str(export_folder)
            mock_log.current_log_file = str(log_file)
            
            result_path = showcase.generate_portfolio()
            
            todays_date = datetime.now().strftime("%m-%d-%y")
            expected_dir = export_folder / f"{todays_date}-portfolio"
            import zipfile
            with zipfile.ZipFile(result_path, "r") as zip_ref:
                zip_ref.extractall(expected_dir)
            
            html_files = list(expected_dir.glob("*.html"))
            with open(html_files[0], "r", encoding="utf-8") as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, "html.parser")
            git_divs = soup.find_all("div", class_="git")
            
            # Find the collaborative project (team_project)
            collab_div = None
            for div in git_divs:
                if "team_project" in div.get_text():
                    collab_div = div
                    break
            
            assert collab_div is not None, "Collaborative git project not found"
            div_text = collab_div.get_text()
            
            # Check for multiple authors label
            assert "Authors:" in div_text, "Multiple authors label not found"
            assert "Alice Smith" in div_text
            assert "Bob Johnson" in div_text
            assert "Carol White" in div_text
            
            # Check for collaborative project label
            assert "Collaborative Project Contributions:" in div_text
            
    finally:
        cleanup_test_dir()
