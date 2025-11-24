import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.log.log_converter import LogConverter
from pathlib import Path
import pandas as pd

class TestLogConverter:

    # Mock file - should also proof that the structure of .logs files can change, and is still robust and usable
    @pytest.fixture
    def sample_csv(self, tmp_path):
        csv_path = tmp_path / "test_log.csv"
        csv_path.write_text("col1,col2\n1,hello\n2,world\n")
        return csv_path

    # Mock file - an empty .csv file as a possibility
    @pytest.fixture
    def empty_csv(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("col1,col2,col3\n")
        return csv_path

    # Test if csv is properly read and loaded
    def test_csv_loading(self, sample_csv):
        lc = LogConverter(str(sample_csv))
        assert isinstance(lc.csv, pd.DataFrame)
        assert list(lc.csv.columns) == ["col1", "col2"]
        assert len(lc.csv) == 2

    # Test if csv is properly read and loaded for empty files
    def test_csv_loading_empty(self, empty_csv):
        lc = LogConverter(str(empty_csv))
        assert len(lc.csv) == 0
        assert lc.data == []
        assert lc.headers == ["col1", "col2", "col3"]

    # Test for the existence and validity of the converted file:
    def test_convert_to_json_creates_file(self, sample_csv):
        lc = LogConverter(str(sample_csv))
        json_path = lc.convert_to_JSON()

        assert Path(json_path).exists()

        content = json.loads(Path(json_path).read_text())
        assert isinstance(content, list)
        assert content[0]["col1"] == 1
        assert content[0]["col2"] == "hello"

    # Test for the .md converter
    def test_convert_to_md_creates_file(self, sample_csv):
        lc = LogConverter(str(sample_csv))
        md_path = lc.convert_to_md()

        assert Path(md_path).exists()
        content = Path(md_path).read_text()
        assert "# Log Data" in content
        assert "hello" in content
        assert "world" in content
        assert "col1" in content
        assert "col2" in content

    # Test for the .pdf converter
    def test_convert_to_pdf_creates_file(self, sample_csv):
        lc = LogConverter(str(sample_csv))
        pdf_path = lc.convert_to_pdf()

        assert Path(pdf_path).exists()
        assert Path(pdf_path).stat().st_size > 0

    # Test for multiple conversion
    def test_all_conversions_work_together(self, sample_csv):
        lc = LogConverter(str(sample_csv))

        json_path = lc.convert_to_JSON()
        md_path = lc.convert_to_md()
        pdf_path = lc.convert_to_pdf()

        assert all(Path(p).exists() for p in [json_path, md_path, pdf_path])

    # Test for proper convertion of the name
    def test_convert_to_json_output_name(self, sample_csv):
        lc = LogConverter(str(sample_csv))
        json_path = lc.convert_to_JSON()

        assert json_path.endswith("_converted.json")
        assert "test_log_converted.json" in json_path

    # Test for non-existing files
    def test_invalid_path_raises(self):
        invalid_path = "nonexistent_file.csv"
        with pytest.raises(FileNotFoundError):
            LogConverter(invalid_path)

    # Test of multiple conversions (appending the convertion - this is solely based of the pandas package) is successful - if it works for one, then works for all
    def test_multiple_conversions(self, sample_csv):
        lc = LogConverter(str(sample_csv))
        p1 = lc.convert_to_JSON()
        p2 = lc.convert_to_JSON()

        assert Path(p1).exists() and Path(p2).exists()
        assert p1 == p2  # same output path each time


