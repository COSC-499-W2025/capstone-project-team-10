import datetime
import os
import pytest
import json
from src.fas import fas
from unittest.mock import MagicMock, patch

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

    def test_git_folder(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
    
        # Mock the GitGrouping class and its methods
        mock_git_grouping = MagicMock()
        mock_git_output = {
            "author": ["Test Author"],
            "title": str(git_dir),
            "subject": "Git Repo",
            "created": "2024-01-01T00:00:00",
            "modified": "2024-01-02T00:00:00",
            "extra data": [
                {
                    "File name": "test.py",
                    "File type": "py",
                    "Last modified": "2024-01-01T00:00:00",
                    "Created time": "2024-01-01T00:00:00",
                    "Extra data": {"language": "python", "libraries": []}
                }
            ],
            "commits": {
                "total_insertions": 10,
                "total_deletions": 5,
                "total_commits": 1,
                "net_change": 5,
                "message_analysis": {"feature"}
            }
        }
        mock_git_grouping.add_repository.return_value = mock_git_output
    
        # Patch GitGrouping in the fas module
        with patch('src.fas.fas_git_grouping.GitGrouping', return_value=mock_git_grouping):
            result = fas.run_fas(str(git_dir))
        
            assert result is not None
            assert result.file_type == "git"
        
            # Check that extra_data contains git grouping information
            assert result.extra_data is not None
            assert isinstance(result.extra_data, dict)
        
            # Verify the structure returned by GitGrouping.add_repository()
            assert "author" in result.extra_data
            assert "title" in result.extra_data
            assert "subject" in result.extra_data
            assert result.extra_data["subject"] == "Git Repo"
            assert "created" in result.extra_data
            assert "modified" in result.extra_data
            assert "extra data" in result.extra_data
            assert "commits" in result.extra_data
        
            # Verify commit analysis structure
            commits = result.extra_data["commits"]
            assert "total_insertions" in commits
            assert "total_deletions" in commits
            assert "total_commits" in commits
            assert "net_change" in commits
            assert "message_analysis" in commits

    def test_importance_exists(self):
        result = fas.run_fas(TEST_FILE)
        assert hasattr(result, "importance")

    def test_importance_is_numeric(self):
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        assert isinstance(result.importance, (int, float))

    def test_extra_data_exists(self):
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        # Check that extra_data is not None
        assert result.extra_data is not None
        # Optionally, check that it's a dict or has expected keys
        if isinstance(result.extra_data, dict):
            # Example: check that key_skills or summary exist
            assert "key_skills" in result.extra_data or "summary" in result.extra_data

    def test_extra_data_is_json_serializable(self):
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        try:
            json_str = json.dumps(result.extra_data)
        except (TypeError, ValueError) as e:
            pytest.fail(f"extra_data is not JSON serializable: {e}")
            
    def test_file_without_extension_is_unknown(self, tmp_path):
        file_path = tmp_path / "pdf"
        file_path.write_text("not a real pdf")

        result = fas.run_fas(str(file_path))

        assert result is not None
        assert result.file_type == "unknown"


    def test_file_with_extension_detected_correctly(self, tmp_path):
        file_path = tmp_path / "test.md"
        file_path.write_text("# Header")

        result = fas.run_fas(str(file_path))

        assert result is not None
        assert result.file_type == "md"


    def test_dotfile_is_unknown(self, tmp_path):
        file_path = tmp_path / ".gitignore"
        file_path.write_text("*.pyc")

        result = fas.run_fas(str(file_path))

        assert result is not None
        assert result.file_type == "unknown"


    def test_makefile_style_name_is_unknown(self, tmp_path):
        file_path = tmp_path / "Makefile"
        file_path.write_text("all:\n\techo hello")

        result = fas.run_fas(str(file_path))

        assert result is not None
        assert result.file_type == "unknown"