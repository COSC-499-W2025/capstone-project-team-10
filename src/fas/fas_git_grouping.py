from pathlib import Path
from fss.repo_reader import Repository
from pydriller import Git
from typing import Optional

class GitGrouping:
    
    def __init__(self):
        self.repositories = {}
        self.files = {}
    
    def add_repository(self, repo_path: str, repo_id: Optional[str] = None):
        repo_path = Path(repo_path).resolve()
        
        # Once a repo has been added, if it does not currently have a repo id, 
        # it will use the path of the repo as its identifier
        if repo_id is None:
            repo_id = str(repo_path)
        
        # Use repo_reader to create a repo object
        repo = Repository(str(repo_path))
        repo.extrapolate()
        
        self.repositories[repo_id] = repo
        self.files[repo_id] = self.get_repo_files(str(repo_path), repo_id)
        
        return self.files[repo_id], repo_id
    
    def get_repo_files(self, repo_path: str, repo_id: Optional[str]):
        try:
            git = Git(repo_path)
            repo_files = git.files()
            
            # Filter out empty strings and strip whitespace
            repo_files = [f.strip() for f in repo_files if f and f.strip()]
            
            output = set()  # A set of the files present within the git repo 
                           # so there are no repeated or wasted analysis/searches
            
            for file in repo_files:
                # TODO: implements file search/file analysis to get the files 
                # return values once they have been implemented
                # output = fss.search(file)
                # output.repo_id = repo_id
                output = None
            
            return repo_files
            
        except Exception as e:
            print(f"[Error] Failed to retrieve files from repository: {type(e).__name__}: {e}")
            return []