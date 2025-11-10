from fss.repo_reader import Repository, run_git_cmd
#import src.fss.fss as fss
import src.fas.fas_git_grouping as git_grouping
import os

test_repo_path = "tests/testdata/test_fes/.git(test)"

class TestGitGrouping:
    def test_repo_id(self):
        output = git_grouping.GitGrouping()
        output = output.add_repository(test_repo_path, None)
        test_data = {
            "logs/refs/heads/master",
            os.path.abspath(test_repo_path),
        }
        assert output == test_data