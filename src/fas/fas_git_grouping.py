from pathlib import Path
#There is an issue here when running tests, for the code to run properly the import path must be "fss.repo_reader" and for the tests to run it must be "src.fss.repo_reader" one or the other does not work depending on the import path and I cannot figure out why.
#Attempting to run the code with src it will return "ModuleNotFoundError: No module named 'src'"
#Attempting to run the tests without src, it will fail and return "ModuleNotFoundError: No module named 'fss'"
from src.fss.repo_reader import Repository, run_git_cmd
#import src.fss.fss as fss
from typing import Optional

class GitGrouping:
    
    def __init__(self):
        self.repositories = {}
        self.files = {}
    
    def add_repository(self, repo_path: str, repo_id: Optional[str]):
        repo_path = Path(repo_path).resolve()
        
        # once a repo has been added, if it does not currently have a repo id, it will use the path of the repo as its identifier
        if repo_id is None:
            repo_id = str(repo_path)
        # use repo_reader to create a repo object
        repo = Repository(str(repo_path))
        repo.extrapolate()
        
        self.repositories[repo_id] = repo
        self.files[repo_id] = self.get_repo_files(str(repo_path), repo_id)
        
        return self.files[repo_id], repo_id
    
    def get_repo_files(self, repo_path: str, repo_id: Optional[str]):
        # This uses the repo_reader in order to get all files within the git file
        files_output = run_git_cmd(repo_path, "lang")
        repo_files = [f.strip() for f in files_output.splitlines() if f.strip()]
        output = set #a set of the files present within the git repo so there are no repeated or wasted analysis/searches
        for file in repo_files:
            #TODO implememnts file search/file analysis to get the files return values once they have been implemented
            #output = fss.search(file)
            #output.repo_id = repo_id
            output = None
        return repo_files