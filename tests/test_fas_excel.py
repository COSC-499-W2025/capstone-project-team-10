import os
import openpyxl
import pytest
from src.fas.fas_excel import extract_excel_data


TESTDATA_DIR = os.path.join("tests", "testdata", "test_fas")
TEST_FILE_PATH = os.path.join(TESTDATA_DIR, "fas_excel_test.xlsx")


def create_excel_test_file():
    # Create a small Excel workbook for testing in the testdata directory.
    os.makedirs(TESTDATA_DIR, exist_ok=True)

    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Summary"
    ws1["A1"] = "Hello"
    ws1["B1"] = "World"

    ws2 = wb.create_sheet("Data")
    ws2["A1"] = 123
    ws2["A2"] = 456

    wb.properties.creator = "Toby"
    wb.properties.lastModifiedBy = "Nguyen"

    wb.save(TEST_FILE_PATH)
    wb.close()

    return TEST_FILE_PATH


def test_extract_excel_data():
    # Ensure extract_excel_data correctly returns Excel metadata.
    file_path = create_excel_test_file()
    metadata = extract_excel_data(file_path)

    assert isinstance(metadata, dict)
    assert "sheet_count" in metadata
    assert "sheet_names" in metadata
    assert "dimensions" in metadata

    # Workbook metadata
    assert metadata["sheet_count"] == 2
    assert set(metadata["sheet_names"]) == {"Summary", "Data"}
    assert metadata["creator"] == "Toby"
    assert metadata["last_modified_by"] == "Nguyen"

    # Sheet dimensions
    dims = metadata["dimensions"]
    assert "Summary" in dims
    assert "Data" in dims
    assert dims["Summary"]["max_row"] >= 1
    assert dims["Data"]["max_row"] >= 2


def test_extract_excel_data_invalid():
    # Ensure function handles invalid Excel files gracefully.
    os.makedirs(TESTDATA_DIR, exist_ok=True)
    bad_file_path = os.path.join(TESTDATA_DIR, "invalid_excel.xlsx")

    with open(bad_file_path, "w") as f:
        f.write("Not a real Excel file")

    metadata = extract_excel_data(bad_file_path)
    assert "error" in metadata
    assert isinstance(metadata["error"], str)
