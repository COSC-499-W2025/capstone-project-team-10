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
        print(logs)
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
        Takes in a (str) repo path, runs a delegated command git log --pretty=format:"%H|%an" (<most recent commit>|<GitHub account associated>)
        to tally the commits done by that author

        Args:
            repo_path (str): The repo's path

        Returns:
            str: the consolidated repo's commit in <hashcommit>|<name>(see below)

        Example:
            >> run_git_log(r"...\pqbao\GitHub\capstone-project-team-10")
            163c26e767400a52ea7ea42b81a8603ea314610a|notbaopham
            f43cf54852225925a1aff8c58dcf1f51b9a5385d|notbaopham
            719667249d7074aec7054f928c625340487cd1ee|notbaopham
            f746ea3fdb9ce57ef83906e6ed15aa5d77840a00|notbaopham
            da988c320fef2b596a07b7ca444e8015bd711dfb|Toby Nguyen
            6609eec5c16f9cce6cffd3812d6315d36dba4e52|Sk3tch7y
            e06e8ecab6af4fe26dcfc43fdec331f110fab3aa|Sk3tch7y
            54def7dc23cb62e0207456a3780acff8000d8590|A-Shrew
            86a8bb68e9df1ddd7389b67962a975956312931f|Sk3tch7y
            d999a85ab356824b327251d398aacc93319a7ff2|Adam Badry
            d144d145c56ee4b7dedcff668f821328bb21576b|Adam Badry
            c550de4ce29bae687a183d3b9bcd6e06ca562d84|Adam Badry
            263db2ce242a980aa756855fcfefeabaf13057d9|Adam Badryd
            ...
    """

    repo = Path(repo_path)

    # Git command format
    if not repo.exists():
        print("Repo not reachable or found")
        return ""

    else:
        if arg == 'logs':
            cmd = ["git", "log", "--pretty=format:%H|%an"]
        else:
            cmd = ["git", "ls-files"]
        try:
            # Creates a subprocess to run the commands for the highest priority
            result = subprocess.run(
                cmd,
                cwd=repo,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()

        # Subprocess error - catching internally errors
        except subprocess.CalledProcessError as e:
            print(f"[Git Error] Command failed with return code {e.returncode}")
            print(f"[Git Error] stderr: {e.stderr.strip() if e.stderr else 'No error message.'}")
            return ""

        # Outer program error - file not found or unreachable, on the machine
        except FileNotFoundError:
            print("[Error] Git is not installed or not found in system PATH.")
            return ""

        # For any other errors
        except Exception as e:
            print(f"[Unexpected Error] {type(e).__name__}: {e}")
            return ""

r'''
repo_path = r"C:\Users\pqbao\GitHub\capstone-project-team-10"
    
        # Run it
testRepo = Repository(repo_path)
testRepo.extrapolate()
print(testRepo.get_authors())
print(testRepo.get_commits_count())
print(testRepo.get_language_dict())
'''