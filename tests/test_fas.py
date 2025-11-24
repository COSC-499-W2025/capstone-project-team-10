import datetime
import os
import pytest
import json
from src.fas import fas

TESTDATA_DIR = os.path.join("tests", "testdata", "test_fas")
TEST_FILE = os.path.join(TESTDATA_DIR, "fas_test_data.docx")


class TestFas:
    def test_run_fas_returns_object(self):
        # run_fas should return a FileAnalysis object
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        assert isinstance(result, fas.FileAnalysis)

    def test_file_name(self):
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        assert result.file_name == "fas_test_data.docx"

    def test_file_type(self):
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        assert result.file_type == "docx"

    def test_last_modified_time(self):
        expected = datetime.datetime.fromtimestamp(
            os.stat(TEST_FILE).st_mtime
        ).isoformat()
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        assert result.last_modified == expected

    def test_created_time(self):
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        assert isinstance(result.created_time, str)
        assert len(result.created_time) > 0

    def test_bad_file_returns_none(self):
        result = fas.run_fas("tests/testdata/test_fas/nonexistent_file_123.docx")
        assert result is None

    def test_git_folder_placeholder(self, tmp_path):
        # A .git folder returns a placeholder FileAnalysis object
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        result = fas.run_fas(str(git_dir))
        assert result is not None
        print(result.file_type)
        print(result.file_name)
        assert result.file_type == "git"
        assert result.file_name == "test_git_folder_placeholder0"
        assert result.extra_data is None

    def test_importance_exists(self):
        result = fas.run_fas(TEST_FILE)
        assert hasattr(result, "importance")

    def test_importance_is_numeric(self):
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        assert isinstance(result.importance, (int, float))
    def test_extra_data_is_json_serializable(self):
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        try:
            json_str = json.dumps(result.extra_data)
        except (TypeError, ValueError) as e:
            pytest.fail(f"extra_data is not JSON serializable: {e}")