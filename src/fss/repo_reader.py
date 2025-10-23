"""
This module provides functionality to read and interact with a file system repository - 
specifically from a determined Git repository.
"""
import subprocess
from pathlib import Path

# Mapping for file type to language extraction - should make this into an updatable public key on GitHub
LANG_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".java": "Java",
    ".rb": "Ruby",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".sh": "Shell",
    ".bat": "Batch",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".m": "Objective-C",
    ".sql": "SQL",
    ".r": "R",
}

"""
    Takes in a (str) file name, extract the suffix and returns the corresponding language from the language mapping above
    
    Args:
        filename (str): The file's name
        
    Returns:
        str: The language that the file's name is in
        
    Example:
        >>> detect_language("draft.py")
        'Python'
        >>> detect_language("front_end.html")
        'HTML'
        >>> detect_language("system_64.dll")
        'Other'
"""
def detect_language(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return LANG_MAP.get(ext, "Other")

"""
    Takes in a (str) repo path, runs a delegated command git log --all --numstat --pretty=format:"%H|%an" (<most recent commit>|<GitHub account associated>)
    and extracts all of the files AND modification that was done
    
    Args:
        repo_path (str): The repo's path
        
    Returns:
        str: the consolidated repo's contents (see below)
        
    Example:
        >>> run_git_log(r'...\pqbao\GitHub\capstone-project-team-10')
        65ce9001cf493115858d9e3614bc7371b8671db6|TobyNguyen710
        22	0	logs/personal logs/Toby/TOBY_LOG.md
        -	-	logs/personal logs/Toby/W7/Done.png
        -	-	logs/personal logs/Toby/W7/Features.png
        -	-	logs/personal logs/Toby/W7/Team_Survey.png
        -	-	logs/personal logs/Toby/W7/Team_Survey_(1).png
        -	-	logs/personal logs/Toby/W7/Team_Survey_(2).png
        -	-	logs/personal logs/Toby/W7/Team_Survey_(3).png

        186a68f9f5db6245c8fc286cac4e14d4bd5faad8|TobyNguyen710
        29	0	logs/team log/TEAM_LOG.md
        -	-	logs/team log/Week7/BurnUpW7.png
        -	-	logs/team log/Week7/CompletedW7.png
        -	-	logs/team log/Week7/InProgressW7.png
        
        da988c320fef2b596a07b7ca444e8015bd711dfb|Toby Nguyen
        c7aac2b2cda4d2bd2ebd6efb9d1ed11e2979a3a3|sfjalex
        -	-	logs/personal logs/Sam/Week7/WeekSevenIssueOne.png
        -	-	logs/personal logs/Sam/Week7/WeekSevenTasks.png
        12	0	logs/personal logs/Sam/sfjalex-PersonalLog.md
        ...
"""
def run_git_log(repo_path: str):

    repo = Path(repo_path)

    # Git command format
    cmd = ["git", "log", "--all", "--numstat", "--pretty=format:%H|%an"]

    # Creates a subprocess to run the commands for the highest priority
    result = subprocess.run(
        cmd,
        cwd=repo,
        capture_output=True,
        text=True,
        check=True
    )

    # Split by lines and return
    return result.stdout.splitlines()


if __name__ == "__main__":
    # 👇 Change this to your actual repo path

    repo_path = r"C:\Users\pqbao\GitHub\capstone-project-team-10"

    # Run it
    lines = run_git_log(repo_path)

    # Preview the first 20 lines
    print("\n".join(lines[:20]))
    print(f"\n✅ Extracted {len(lines)} lines from {repo_path}")

