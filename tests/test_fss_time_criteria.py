import pytest
import datetime
import src.fss.fss_helper as fss_helpers
from unittest.mock import patch, MagicMock
from pathlib import Path

class TestFssTimeCriteria:

    # If the str_path_converter works with str
    def test_str_path_converter_with_str(self):
        path_str = "example.txt"
        result = fss_helpers.str_path_converter(path_str)
        assert isinstance(result, Path)
        assert result.name == "example.txt"

    # If the str_path_converter works with path
    def test_str_path_converter_with_path(self):
        path_obj = Path("another.txt")
        result = fss_helpers.str_path_converter(path_obj)
        assert result is path_obj  # should return same object

    # If the get_creation_time properly extracts the time
    @patch.object(Path, "stat")
    def test_get_creation_time(self, mock_stat):
        fake_time = datetime.datetime(2025, 11, 1, 12, 0, 0)
        mock_result = MagicMock()
        mock_result.st_birthtime = fake_time.timestamp()  # main target
        mock_result.st_ctime = fake_time.timestamp()  # fallback
        mock_stat.return_value = mock_result

        result = fss_helpers.get_creation_time("dummy.txt")
        assert isinstance(result, datetime.datetime)
        assert result == fake_time

    @patch.object(Path, "stat")
    def test_get_mod_time(self, mock_stat):
        fake_time = datetime.datetime(2025, 11, 1, 12, 0, 0)
        mock_result = MagicMock()
        mock_result.st_mtime = fake_time.timestamp()  # this is the key
        mock_stat.return_value = mock_result

        result = fss_helpers.get_mod_time("dummy.txt")
        assert isinstance(result, datetime.datetime)
        assert result == fake_time

    @patch.object(fss_helpers, "get_creation_time")
    def test_time_check_both_bounds(self, mock_get_creation):
        mock_get_creation.return_value = datetime.datetime(2025, 11, 1, 12, 0, 0)
        lower = datetime.datetime(2025, 10, 1)
        upper = datetime.datetime(2025, 12, 1)
        assert fss_helpers.time_check([lower, upper], "dummy.txt", "create") is True

    @patch.object(fss_helpers, "get_mod_time")
    def test_time_check_upper_bound_only(self, mock_get_mod):
        mock_get_mod.return_value = datetime.datetime(2025, 11, 1, 12, 0, 0)
        upper = datetime.datetime(2025, 12, 1)
        assert fss_helpers.time_check([None, upper], "dummy.txt", "mod") is True

    @patch.object(fss_helpers, "get_mod_time")
    def test_time_check_lower_bound_only(self, mock_get_mod):
        mock_get_mod.return_value = datetime.datetime(2025, 11, 1, 12, 0, 0)
        lower = datetime.datetime(2025, 10, 1)
        # Should return True since no upper bound
        assert fss_helpers.time_check([lower, None], "dummy.txt", "mod") is True

    @patch.object(fss_helpers, "get_creation_time")
    def test_time_check_no_bounds(self, mock_get_creation):
        mock_get_creation.return_value = datetime.datetime(2025, 11, 1)
        # No bounds at all → always True
        assert fss_helpers.time_check([None, None], "dummy.txt", "create") is True
