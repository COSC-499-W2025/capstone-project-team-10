"""
    This module provides functionality to read and interact with a file system repository -
    specifically from a determined Git repository.
"""
import subprocess
from pathlib import Path

class Repository:
    """
        This class provides as an object as a Repo to be an information medium, with necessary methods and storage attributes.
        Just pluck what you need out of them
    """

    def __init__(self, rpath):
        """
            Constructor for Repository class - holds:

            Attributes:
                @path: The absolute path of the repo folder
                @authors: A dictionary, with authors as {keys} and the list associated with the key as the commits made by that author {value}
                @language: A dictionary, with languages as {keys} and the value associated with the key are the amounts of files associated with that language {value}

        """
        self.path = rpath
        self.authors = {}
        self.language = {}

    def extrapolate(self):
        """
            The processor for the object Repository.

            Using the repo path, the file:
                1. Extract the logs of commits from git logs --pretty=format:"%H|%an"
                2. Process line by line and appends the logs by name
                3. Extract the files directory from git ls-files
                4. Process line by line and tally the extensions towards its respective language

            !Use right after creating a Repository object!
        """
        # parse commit log (format: "<hash>|<author>")
        logs = run_git_cmd(self.path, "logs")
        for line in logs.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 1)
            if len(parts) != 2:
                continue
            commit_hash, author = parts[0].strip(), parts[1].strip()
            self.authors.setdefault(author, []).append(commit_hash)

        # parse tracked files and map extensions to languages
        files_out = run_git_cmd(self.path, "lang")
        lang_counts = {}
        for f in files_out.splitlines():
            f = f.strip()
            if not f:
                continue
            ext = Path(f).suffix.lower()
            lang = LANG_MAP.get(ext, "Others")
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        self.language = lang_counts

    def get_authors(self):
        """
            Returns the list of authors in the format of a readily-process list

            Returns:
                [list] as list of authors contributed within the repo
        """
        authors_list = []
        for author_keys in self.authors:
            authors_list.append(author_keys)
        return authors_list

    def get_commits_count(self):
        """
            Returns a dictionary that contains the authors as the keys and the int value as the amount of commits done by that author

            Returns:
                (dict) with authors and int value, tallying the counts of commits done
        """
        list_authors_keys = self.get_authors()
        dict_authors_commits = {}
        for list_author_key in list_authors_keys:
            dict_authors_commits[list_author_key] = len(self.authors[list_author_key])
        return dict_authors_commits

    def get_language_dict(self):
        """
            Returns the dictionary with language - tally of files in that language key-value

            Returns:
                (dict) with {key} as the language and {value} as the amount of files in that format
        """
        return self.language

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

def detect_language(filename: str) -> str:
    """
        Takes in a (str) file name, extract the suffix and returns the corresponding language from the language mapping above

        Args:
            filename (str): The file's name

        Returns:
            str: The language that the file's name is in

        Example:
            >> detect_language("draft.py")
            'Python'
            >> detect_language("front_end.html")
            'HTML'
            >> detect_language("system_64.dll")
            'Other'
    """
    ext = Path(filename).suffix.lower()
    return LANG_MAP.get(ext, "Other")

def run_git_cmd(repo_path: str, arg) -> str:
    r"""
        Takes in a (str) repo path, runs a delegated command git log --all --numstat --pretty=format:"%H|%an" (<most recent commit>|<GitHub account associated>)
        and extracts all of the files AND modification that was done

        Args:
            repo_path (str): The repo's path

        Returns:
            str: the consolidated repo's contents (see below)

        Example:
            >> run_git_log(r'...\pqbao\GitHub\capstone-project-team-10')
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

    repo = Path(repo_path)

    # Git command format
    if arg == 'logs':
        cmd = ["git", "log", "--pretty=format:%H|%an"]
    else:
        cmd = ["git", "ls-files"]

    # Creates a subprocess to run the commands for the highest priority
    result = subprocess.run(
        cmd,
        cwd=repo,
        capture_output=True,
        text=True,
        check=True
    )

    # Split by lines and return
    return result.stdout.strip()


if __name__ == "__main__":
    print("Welcome to repo reader")
r'''
    # Change this to your actual repo path
    # 👇
    repo_path = r"C:\Users\pqbao\GitHub\capstone-project-team-10"

    # Run it
    testRepo = Repository(repo_path)
    testRepo.extrapolate()
    print(testRepo.get_authors())
    print(testRepo.get_commits_count())
    print(testRepo.get_language_dict())
'''