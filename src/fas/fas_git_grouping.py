from pathlib import Path
from src.fss.repo_reader import Repository
import src.fas.fas as fas
from pydriller import Git, Repository as PyDrillerRepo
from typing import Optional, List, Dict
import os
import src.param.param as param

class GitGrouping:
    
    def __init__(self):
        self.repositories = {}
        self.files = {}
        self.commits = {}  
    
    def add_repository(self, repo_path: str, repo_id: Optional[str] = None):
        repo_path = Path(repo_path).resolve()
        
        # Once a repo has been added, if it does not currently have a repo id, 
        # it will use the path of the repo as its identifier
        if repo_id is None:
            repo_id = str(repo_path)
        
        # Use repo_reader to create a repo object
        repo = Repository(str(repo_path), filter_author = param.get("scan.github_username"))
        repo.extrapolate()
        
        self.repositories[repo_id] = repo

        # Get files analysis for extra data
        extra_data = self.get_repo_files(str(repo_path), repo_id)
        self.files[repo_id]  = extra_data

        # Store commit data
        commit_data = repo.get_commits_content()
        self.commits[repo_id] = commit_data

        commit_analyzed = self.commit_analysis(commit_data)

        # Extract created and modified dates from Git history
        created_date, modified_date = self.get_repo_dates(str(repo_path))
        
        # Build the git_output object with all required fields
        git_output = {
            "author": repo.get_authors(),
            "title": repo_id, # Repo ID becomes the title of the project
            "subject": "Git Repo",
            "created": created_date,
            "modified": modified_date,
            "extra data": extra_data,
            "commits": commit_analyzed,
        }
        
        return git_output
    
    def get_repo_files(self, repo_path: str, repo_id: Optional[str] = None):
        # Retrieve all files from the repository and run file analysis on each.
        try:
            # Remove .git suffix if present
            project_path = repo_path[:-4] if repo_path.endswith('.git') else repo_path
            git = Git(project_path)
            repo_files = git.files()
            print(repo_files)
            print("\n")
            
            # Filter out empty strings and strip whitespace
            repo_files = [f.strip() for f in repo_files if f and f.strip()]
            print(repo_files)
            print("\n")
            
            # A set of the files present within the git repo so there are no repeated or wasted analysis/searches
            output = []  

            print(project_path)
            print("\n")
            
            for file in repo_files:
                # Get file path to each file in the repo
                file_path = os.path.join(project_path, file)
                print(file_path)
                
                # Only analyze if is a file and exists
                if os.path.isfile(file_path):
                    file_result = fas.run_fas(file_path)
                    
                    # Add result to output, which will be added to the returned project file attached in extra data
                    if file_result is not None:
                        output.append({
                            "File name": file_result.file_name,
                            "File type": file_result.file_type,
                            "Last modified": file_result.last_modified,
                            "Created time": file_result.created_time,
                            "Extra data": file_result.extra_data,
                        })
            
            return output
            
        except Exception as e:
            print(f"[Error] Failed to retrieve files from repository: {type(e).__name__}: {e}")
            return set()
        
    def get_repo_dates(self, repo_path: str) -> tuple:
        # Extract the creation date (first commit) and last modification date (most recent commit) from the repository.
        try:
            commits = list(PyDrillerRepo(repo_path).traverse_commits())
            
            if not commits:
                return None, None
            
            # Commits are in reverse chronological order by default, Most recent commit is first, oldest is last
            modified_date = commits[0].committer_date
            created_date = commits[-1].committer_date
            
            return created_date, modified_date
            
        except Exception as e:
            print(f"[Error] Failed to extract repository dates: {type(e).__name__}: {e}")
            return None, None
        
    def commit_analysis(self, commit_data):
        # Analyze commit data to extract insights from messages and calculate total changes.
        if not commit_data:
            return {
                "total_insertions": 0,
                "total_deletions": 0,
                "total_commits": 0,
                "message_analysis": {}
            }
        total_insertions = 0
        total_deletions = 0
        messages = []
    
        # Process each commit
        for commit in commit_data:
            # Sum up insertions and deletions
            total_insertions += commit.get('insertions', 0)
            total_deletions += commit.get('deletions', 0)
        
            # Collect commit messages
            msg = commit.get('message', '').strip()
            if msg:
                messages.append(msg)
    
        output = {
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "total_commits": len(commit_data),
            "net_change": total_insertions - total_deletions,
            "message_analysis": self._categorize_messages(messages),
        }

        return output

    def _categorize_messages(self, messages):
        #Categorize commit messages by type for analysis
        output = set()
        for msg in messages:
            msg_lower = msg.lower()
        
            if any(word in msg_lower for word in ['fix', 'bug', 'patch', 'resolve']):
                output.add("fix")
            elif any(word in msg_lower for word in ['add', 'feature', 'new', 'implement']):
                output.add("feature")
            elif any(word in msg_lower for word in ['doc', 'readme', 'comment']):
                output.add("docs")
            elif any(word in msg_lower for word in ['refactor', 'restructure', 'reorganize']):
                output.add("refactor")
            elif any(word in msg_lower for word in ['test', 'spec', 'coverage', 'tests']):
                output.add("test")
            elif any(word in msg_lower for word in ['style', 'format', 'lint']):
                output.add("style")
            else:
                output.add("other")

        
        return output