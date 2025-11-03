import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.fss.repo_reader import detect_language, LANG_MAP, run_git_cmd, Repository

class TestRepoReader:

    # If the method properly maps the language to the suffix
    def test_detect_language_known(self):
        assert detect_language("script.py") == "Python"
        assert detect_language("index.html") == "HTML"


    # If the method properly maps the language to the suffix - other cases
    def test_detect_language_unknown(self):
        assert detect_language("archive.xyz") == "Other"


    # If the method properly runs the git command line - testing for "logs" arguments (<commit_hash>|<author>)
    @patch("src.fss.repo_reader.subprocess.run")
    def test_run_git_cmd_logs(self, mock_run, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = "abc123|Author One\ndef456|Author Two"
        mock_run.return_value = mock_result

        repo = tmp_path
        result = run_git_cmd(repo, "logs")

        mock_run.assert_called_once_with(
            ["git", "log", "--pretty=format:%H|%an"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True
        )
        assert "Author One" in result
        assert "abc123" in result

    # If the method properly runs the git command line - testing for "langs" arguments (<repo_path{.suffix_lang}>)
    @patch("src.fss.repo_reader.subprocess.run")
    def test_run_git_cmd_lang(self, mock_run, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = "main.py\nindex.html"
        mock_run.return_value = mock_result

        repo = tmp_path
        result = run_git_cmd(repo, "lang")

        mock_run.assert_called_once_with(
            ["git", "ls-files"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True
        )
        assert "main.py" in result
        assert "index.html" in result

    # If the git command properly detects a faulty Path to the repo - revise repo_reader.py line 202
    def test_run_git_cmd_repo_not_exist(self, tmp_path):
        fake_path = tmp_path / "nonexistent"
        result = run_git_cmd(fake_path, "logs")
        assert result == ""

    # If the git command properly detects a FileNotFoundError - revise repo_reader.py line 208
    @patch("src.fss.repo_reader.subprocess.run", side_effect=FileNotFoundError)
    def test_run_git_cmd_git_not_found(self, mock_run, tmp_path):
        result = run_git_cmd(tmp_path, "logs") #TODO: adding a type checker here - it is displaying potential type pollution
        assert result == ""

    # If the extrapolate() method on a Repository class object works - a general results
    @patch("src.fss.repo_reader.run_git_cmd")
    def test_extrapolate_parsing(self, mock_run_git_cmd, tmp_path):
        # Mock results:
        mock_run_git_cmd.side_effect = [
            "abc123|Author1\ndef456|Author1\nxyz789|Author2",
            "main.py\nindex.html\nutils.cpp\nnotes.txt"
        ]

        repo = Repository(tmp_path)
        repo.extrapolate()

        # Authors
        assert "Author1" in repo.authors
        assert len(repo.authors["Author1"]) == 2
        assert "Author2" in repo.authors

        # Language dictionary
        langs = repo.get_language_dict()
        assert langs["Python"] == 1 # main.py
        assert langs["HTML"] == 1 # index.html
        assert langs["C++"] == 1 # utils.cpp
        assert langs["Others"] == 1  # notes.txt

    # Authors attribute
    def test_get_authors(self):
        repo = Repository("dummy")
        repo.authors = {"Alice": ["a1"], "Bob": ["b1", "b2"]}
        result = repo.get_authors()
        assert sorted(result) == ["Alice", "Bob"]

    # Commit counts attribute
    def test_get_commits_count(self):
        repo = Repository("dummy")
        repo.authors = {"Alice": ["a1"], "Bob": ["b1", "b2", "b3"]}
        result = repo.get_commits_count()
        assert result == {"Alice": 1, "Bob": 3}

    # Language dict attribute
    def test_get_language_dict(self):
        repo = Repository("dummy")
        repo.language = {"Python": 10, "C++": 3}
        assert repo.get_language_dict() == {"Python": 10, "C++": 3}