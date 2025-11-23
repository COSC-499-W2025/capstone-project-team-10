from pydriller import Repository as PyDrillerRepo
from pathlib import Path
from collections import defaultdict

class Repository:

    def __init__(self, rpath):
        self.path = rpath
        self.authors = {}
        self.language = {}

    def extrapolate(self):
        # Extract commit and file information using PyDriller.
        try:
            # Parse commits and authors
            for commit in PyDrillerRepo(self.path).traverse_commits():
                author = commit.author.name
                commit_hash = commit.hash
                self.authors.setdefault(author, []).append(commit_hash)

            # Parse tracked files and map extensions to languages
            lang_counts = defaultdict(int)
            
            # Get files from the latest commit
            for commit in PyDrillerRepo(self.path, only_in_branch='HEAD').traverse_commits():
                for modified_file in commit.modified_files:
                    if modified_file.new_path:
                        ext = Path(modified_file.new_path).suffix.lower()
                        lang = LANG_MAP.get(ext, "Others")
                        lang_counts[lang] += 1
                break

            self.language = dict(lang_counts)

        except Exception as e:
            print(f"Failed to analyze repository: {type(e).__name__}: {e}")
            self.authors = {}
            self.language = {}

    def get_authors(self):
        # Return list of all authors.
        return list(self.authors.keys())

    def get_commits_count(self):
        # Return dictionary of authors and their commit counts.
        return {author: len(commits) for author, commits in self.authors.items()}

    def get_language_dict(self):
        # Return dictionary of languages and file counts.
        return self.language


# Mapping for file type to language extraction
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
    # Detect language from filename extension.
    ext = Path(filename).suffix.lower()
    return LANG_MAP.get(ext, "Other")