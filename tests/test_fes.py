import pytest
import src.fes.fes_app as fes
from unittest.mock import patch

repoCommits = "tests/testdata/test_fes/.git(test)/logs/refs/heads/master"

class TestFes:
    def test_fes_gitUser(self):
        #TODO: update fes to collect usernames from .git files
        with patch('builtins.print') as mock_print:
            fes.fes_users(repoCommits)
            # response shall be the user names that created the commits
            mock_print.assert_called_with("userName")

    def test_fes_gitCommits(self):
        #TODO: update fes to collect commits made from .git files
        result = fes.fes_commits(repoCommits)
        # response shall be the number of commits made within the .git files.
        assert result == "5"
            