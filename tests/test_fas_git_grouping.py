import src.fas.fas_git_grouping as git_grouping
from src.fss.repo_reader import detect_language, LANG_MAP, run_git_cmd, Repository
import os

test_repo_path = "tests/testdata/test_fes/.git(test)"

class TestGitGrouping:
    def test_add_repo(self):
        output = git_grouping.GitGrouping()
        output = output.add_repository(test_repo_path, None)
        files = [
            'bob_likes_this.txt', 
            'logs/refs/heads/master', 
            'some_code_testdata.py'
        ]
        test_data = (
            files,
            os.path.abspath(test_repo_path),
        )
        assert output == test_data

    def test_get_repo_files(self):
        output = git_grouping.GitGrouping()
        output = output.get_repo_files(test_repo_path, None)
        files = [
            'bob_likes_this.txt', 
            'logs/refs/heads/master', 
            'some_code_testdata.py'
        ]
        assert output == files