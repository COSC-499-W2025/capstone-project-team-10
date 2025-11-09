from pathlib import Path
from fss.repo_reader import Repository, run_git_cmd

class GitGrouping:
    
    def __init__(self):
        self.repositories = {}
        self.file_groups = {}
    
    def add_repository(self, repo_path: str, repo_id: str = None):
        repo_path = Path(repo_path).resolve()
        
        # Use directory name as default ID
        if repo_id is None:
            repo_id = repo_path.name
        
        # Create and populate Repository object
        repo = Repository(str(repo_path))
        repo.extrapolate()
        
        self.repositories[repo_id] = repo
        self.file_groups[repo_id] = self.get_repo_files(str(repo_path))
        
        return repo_id
    
    def get_repo_files(self, repo_path: str):
        # This uses the repo_reader in order to 
        files_output = run_git_cmd(repo_path, "lang")
        print(files_output)
        return [f.strip() for f in files_output.splitlines() if f.strip()]

    