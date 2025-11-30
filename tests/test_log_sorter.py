import os
import pytest
import pandas as pd
from unittest.mock import patch, mock_open
from pathlib import Path
import tempfile
from src.log.log_sorter import LogSorter


class TestLogSorter:

    # Mock CSV file with sample data
    @pytest.fixture
    def sample_csv(self, tmp_path):
        csv_content = """File path analyzed,File name,File type,Last modified,Created time,Extra data,Importance
    tests/testdata/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,EXTRA DATA,0.0
    tests/testdata/file2.txt,file2.txt,txt,2023-10-02T12:00:00,2023-09-29T11:00:00,EXTRA EXTRA DATA,1.0
    tests/testdata/file3.pdf,file3.pdf,pdf,2023-10-03T12:00:00,2023-09-28T11:00:00,PDF CONTENT,0.5"""

        csv_path = tmp_path / "test_log.csv"
        csv_path.write_text(csv_content)
        return csv_path

    # Empty CSV file
    @pytest.fixture
    def empty_csv(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("File path analyzed,File name,File type,Last modified,Created time,Extra data,Importance\n")
        return csv_path

    # Test initialization and CSV loading
    def test_initialization(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        assert isinstance(sorter.log, pd.DataFrame)
        assert len(sorter.log) == 3
        assert sorter.params == []
        assert sorter.ascending == []

    # Test get_available_columns excludes Extra data
    def test_get_available_columns(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        available_columns = sorter.get_available_columns()

        assert "Extra data" not in available_columns
        assert "File name" in available_columns
        assert "Importance" in available_columns
        assert len(available_columns) == 6  # All columns except Extra data

    # Test set_sort_parameters with valid single column
    def test_set_sort_parameters_single_column(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        sorter.set_sort_parameters(["File name"], [True])

        assert sorter.params == ["File name"]
        assert sorter.ascending == [True]

    # Test set_sort_parameters with valid multiple columns
    def test_set_sort_parameters_multiple_columns(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        sorter.set_sort_parameters(["Importance", "File name"], [False, True])

        assert sorter.params == ["Importance", "File name"]
        assert sorter.ascending == [False, True]

    # Test set_sort_parameters with default ascending
    def test_set_sort_parameters_default_ascending(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        sorter.set_sort_parameters(["File name", "File type"])

        assert sorter.ascending == [True, True]

    # Test set_sort_parameters rejects Extra data column
    def test_set_sort_parameters_rejects_extra_data(self, sample_csv):
        sorter = LogSorter(str(sample_csv))

        with pytest.raises(ValueError, match = "Cannot sort by 'Extra data' column"):
            sorter.set_sort_parameters(["Extra data"], [True])

    # Test set_sort_parameters rejects non-existent column
    def test_set_sort_parameters_rejects_invalid_column(self, sample_csv):
        sorter = LogSorter(str(sample_csv))

        with pytest.raises(ValueError, match = "Column 'Nonexistent' not found"):
            sorter.set_sort_parameters(["Nonexistent"], [True])

    # Test set_sort_parameters rejects empty parameters
    def test_set_sort_parameters_rejects_empty_list(self, sample_csv):
        sorter = LogSorter(str(sample_csv))

        with pytest.raises(ValueError, match = "Parameters list cannot be empty"):
            sorter.set_sort_parameters([], [])

    # Test set_sort_parameters rejects mismatched lengths
    def test_set_sort_parameters_rejects_length_mismatch(self, sample_csv):
        sorter = LogSorter(str(sample_csv))

        with pytest.raises(ValueError, match = "Number of order flags.*must match"):
            sorter.set_sort_parameters(["File name", "File type"], [True])

    # Test sort without parameters raises error
    def test_sort_without_parameters_raises_error(self, sample_csv):
        sorter = LogSorter(str(sample_csv))

        with pytest.raises(ValueError, match = "No sorting parameters set"):
            sorter.sort()

    # Test sort with single column
    def test_sort_single_column(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        sorter.set_sort_parameters(["Importance"], [False])  # Descending

        result = sorter.sort()

        # Should be sorted by Importance descending: 1.0, 0.5, 0.0
        assert result.iloc[0]["Importance"] == 1.0
        assert result.iloc[1]["Importance"] == 0.5
        assert result.iloc[2]["Importance"] == 0.0

    # Test sort with multiple columns (tie-breaking)
    def test_sort_multiple_columns(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        sorter.set_sort_parameters(["File type", "Importance"], [True, False])

        result = sorter.sort()

        # Should be sorted by File type ascending, then Importance descending within same type
        assert len(result) == 3

    # Test get_preview without parameters raises error
    def test_get_preview_without_parameters_raises_error(self, sample_csv):
        sorter = LogSorter(str(sample_csv))

        with pytest.raises(ValueError, match = "No sorting parameters set"):
            sorter.get_preview()

    # Test get_preview returns correct data
    def test_get_preview_returns_data(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        sorter.set_sort_parameters(["File name"], [True])

        preview = sorter.get_preview(2)

        assert isinstance(preview, pd.DataFrame)
        assert len(preview) == 2  # Only 2 rows as requested

    # Test get_preview doesn't modify original data
    def test_get_preview_preserves_original_data(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        original_data = sorter.log.copy()

        sorter.set_sort_parameters(["File name"], [True])
        preview = sorter.get_preview()

        # Original data should not be sorted
        pd.testing.assert_frame_equal(sorter.log, original_data)

    # Test return_csv creates new file
    def test_return_csv_creates_file(self, sample_csv):
        sorter = LogSorter(str(sample_csv))
        sorter.set_sort_parameters(["File name"], [True])
        sorter.sort()

        csv_output = sorter.return_csv()

        # Check that file was created with _sorted suffix
        expected_path = sample_csv.parent / "test_log_sorted.csv"
        assert expected_path.exists()

        # Check that CSV string is returned
        assert isinstance(csv_output, str)
        assert "File path analyzed" in csv_output

    # Test initialization with non-existent file
    def test_initialization_with_invalid_path(self):
        with pytest.raises(FileNotFoundError):
            LogSorter("nonexistent_file.csv")

    # Test with empty CSV file
    def test_empty_csv_file(self, empty_csv):
        sorter = LogSorter(str(empty_csv))

        assert len(sorter.log) == 0
        assert sorter.get_available_columns() == ["File path analyzed", "File name", "File type", "Last modified", "Created time", "Importance"]
        sorter.set_sort_parameters(["File name"], [True])         # call method - should still work
        preview = sorter.get_preview()
        assert len(preview) == 0