import csv
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

import src.log.log as log
import src.param.param as param
from src.fas.fas import FileAnalysis

resume_entry_template = """
{project_name} - {project_type}
Date: {created_time} to {last_modified}"""

portfolio_entry_template = """
<div class='{file_type}'>
  <h2><a href={new_file_path} >{file_name}</a> - {file_type_upper}</h2>
  <h3>Date Active: {created} to {modified}</h3>
  {details}
</div>
<hr/>
"""

image_types = [
    "jpeg",
    "jpg",
    "png",
    "gif",
    "webp",
    "tiff",
    "bmp",
    "heif",
    "heic",
    "avif",
]

collaborative_types = ["git"]


def format_last_modified(file_analysis: FileAnalysis) -> str:
    last_modified = datetime.fromisoformat(file_analysis.last_modified)
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)

    if last_modified > one_month_ago:
        return "Current"
    else:
        # Format as you like, e.g., "YYYY-MM-DD"
        return last_modified.strftime("%Y-%m-%d")


def format_created_time(file_analysis: FileAnalysis) -> str:
    created_time = datetime.fromisoformat(file_analysis.created_time)
    return created_time.strftime("%Y-%m-%d")


def generate_all():
    generate_resume()
    generate_portfolio()


def generate_resume():
    todays_date: str = datetime.now().strftime("%m-%d-%y")
    export_path: Path = Path(param.export_folder_path) / (todays_date + "-resume.pdf")
    file_number: int = 0
    # Ensure unique file name
    while export_path.exists():
        file_number += 1
        export_path = Path(param.export_folder_path) / (
            todays_date + f"-resume-{file_number}.pdf"
        )

    log_file: Path = Path(log.current_log_file)
    if not export_path.parent.exists():
        print(f"Export folder does not exist: {export_path}")
        return
    try:
        with open(log_file, "r") as lf:
            reader = csv.reader(lf)
            pdf_output = FPDF()
            pdf_output.add_page()
            pdf_output.set_font("Times", size=14)
            # For each row in the log file, create an entry in the resume
            # Skip the first row as it is a header
            next(reader)  # Skip header
            for row in reader:
                file_analysis: FileAnalysis = FileAnalysis(
                    row[0], row[1], row[2], row[3], row[4], row[5]
                )
                entry_headers: str = (
                    resume_entry_template.format(
                        project_name=file_analysis.file_name,
                        project_type=file_analysis.file_type.upper(),
                        created_time=format_created_time(file_analysis),
                        last_modified=format_last_modified(file_analysis),
                    )
                    + "\n"
                )
                header_font_size: int = 18
                for line in entry_headers.splitlines():
                    pdf_output.set_font("Times", size=header_font_size, style="B")
                    pdf_output.cell(0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    header_font_size -= 2

                pdf_output.set_font("Times", size=14)
                # Change additional details based on file type
                match file_analysis.file_type:
                    case file_type if file_type in image_types:
                        # The Square brackets are used to denote the path for inclusion in pdf and web formats
                        pdf_output.cell(
                            0,
                            10,
                            f"Artistic Project: [Insert Description]",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )
                        pdf_output.image(
                            file_analysis.file_path, w=100
                        )  # x, y = position; w = width in mm

                    case file_type if file_type in collaborative_types:
                        pdf_output.cell(
                            0,
                            10,
                            f"Project Contributions: {file_analysis.extra_data}",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )
                        # TODO: Expand to include more details about the files in the git project
                    case _:
                        # Assume this is the text file and the extra data is the key skills used
                        pdf_output.cell(
                            0,
                            10,
                            f"Key Skills demonstrated in this project: {file_analysis.extra_data}",
                            new_x=XPos.LMARGIN,
                            new_y=YPos.NEXT,
                        )
                pdf_output.ln(10)  # Add a line break between entries
            pdf_output.output(str(export_path))
    except Exception as e:
        print(f"Something went wrong: {e}")
        return


def generate_portfolio():
    todays_date: str = datetime.now().strftime("%m-%d-%y")
    portfolio_export_path_dir: Path = Path(param.export_folder_path) / (
        todays_date + "-portfolio"
    )
    portfolio_export_zip_path_dir: Path = Path(param.export_folder_path) / (
        todays_date + "-portfolio.zip"
    )
    file_number: int = 0

    while portfolio_export_path_dir.exists() or portfolio_export_zip_path_dir.exists():
        file_number += 1
        portfolio_export_path_dir = Path(param.export_folder_path) / (
            todays_date + f"-portfolio-{file_number}"
        )
        portfolio_export_zip_path_dir = Path(param.export_folder_path) / (
            todays_date + f"-portfolio-{file_number}.zip"
        )

    portfolio_export_path_dir.mkdir(parents=True, exist_ok=True)

    portfolio_export_resource_path: Path = portfolio_export_path_dir / ("resources")
    portfolio_export_resource_path.mkdir(parents=True, exist_ok=True)

    portfolio_export_path: Path = portfolio_export_path_dir / (
        todays_date + "-portfolio.html"
    )
    log_file: Path = Path(log.current_log_file)
    if not portfolio_export_path_dir.exists():
        print(f"Export folder does not exist: {portfolio_export_path}")
        return
    try:
        with open(log_file, "r") as lf:
            with open(portfolio_export_path, "w") as portfolio:
                portfolio.write("<html><head><title>Portfolio</title></head><body>\n")
                portfolio.write("<h1>Project Portfolio</h1>\n")
                reader = csv.reader(lf)
                # Create an entry for each row in the log file
                #  # Skip the first row as it is a header
                next(reader)  # Skip header
                for row in reader:
                    file_analysis = FileAnalysis(*row)
                    # Move all files to resources folder
                    file_analysis_source = Path(file_analysis.file_path)
                    shutil.copy(
                        file_analysis_source,
                        portfolio_export_resource_path
                        / (file_analysis.file_name + "." + file_analysis.file_type),
                    )
                    # Change details based on file type
                    if file_analysis.file_type in image_types:
                        details = f"<p>Artistic Project:</p><img src='resources/{file_analysis.file_name}.{file_analysis.file_type}' alt='{file_analysis.file_name}' width='300'/>"
                    elif file_analysis.file_type in collaborative_types:
                        details = (
                            f"<p>Project Contributions: {file_analysis.extra_data}</p>"
                        )
                    else:
                        details = f"<p>Key Skills demonstrated in this project: {file_analysis.extra_data}</p>"
                    # write details to portfolio
                    portfolio.write(
                        portfolio_entry_template.format(
                            new_file_path=f"resources/{file_analysis.file_name}.{file_analysis.file_type}",
                            file_type=file_analysis.file_type,
                            file_name=file_analysis.file_name,
                            file_type_upper=file_analysis.file_type.upper(),
                            created=format_created_time(file_analysis),
                            modified=format_last_modified(file_analysis),
                            details=details,
                        )
                    )
                portfolio.write("</body></html>\n")
        # Create ZIP Archive, and delete the unzipped folder
        shutil.make_archive(
            str(portfolio_export_path_dir), "zip", root_dir=portfolio_export_path_dir
        )
        shutil.rmtree(portfolio_export_path_dir)

    except Exception as e:
        print(f"Failed to read log file: {e}")
        return
