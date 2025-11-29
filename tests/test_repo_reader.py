import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.fss.repo_reader import detect_language, LANG_MAP, Repository

class MockAuthor:
    # Mocks the author object from pydriller
    def __init__(self, name):
        self.name = name

class MockModifiedFile:
    # Mocks the ModifiedFile object from pydriller
    def __init__(self, new_path):
        self.new_path = new_path

class MockCommit:
    # Mock commits for the PyDriller object
    def __init__(self, commit_hash, author_name, modified_files_list):
        self.hash = commit_hash
        self.author = MockAuthor(author_name)
        self.modified_files = [MockModifiedFile(p) for p in modified_files_list]

# Set up commit data to be used later in tests.
MOCK_COMMITS_DATA = [
    MockCommit('c_hash1', 'Author A', ['src/file1.py', 'src/app.js']),
    MockCommit('c_hash2', 'Author B', ['index.html']),
    MockCommit('c_hash3', 'Author A', ['api/core.ts', 'tests/test_2.py', 'data/config.xyz']),
    MockCommit('c_hash4', 'Author C', ['old_file.java']),
]
MOCK_LATEST_COMMIT = MOCK_COMMITS_DATA[-2]

# Used to mock the PyDrillerRepo class for the tests
@pytest.fixture
def mock_pydriller_repo():
    def factory(path, only_in_branch=None):
        mock_repo_instance = MagicMock()
        
        if only_in_branch == 'HEAD':
            # This is the call for language detection, only the latest commit is returned.
            mock_repo_instance.traverse_commits.return_value = [MOCK_LATEST_COMMIT]
        else:
            # This is the call for author/commit counting, all commits are returned.
            mock_repo_instance.traverse_commits.return_value = MOCK_COMMITS_DATA
        
        return mock_repo_instance
    return factory

# Tests that the content of the repo (author, commits, file extensions) is correct
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_repository_extrapolate_success(mock_repo_class, mock_pydriller_repo):

    mock_repo_class.side_effect = mock_pydriller_repo

    repo = Repository("/mock/path")
    repo.extrapolate()

    # Test Authors and Commits
    expected_commit_counts = {
        'Author A': 2,
        'Author B': 1,
        'Author C': 1, 
    }
    assert repo.get_authors() == sorted(list(expected_commit_counts.keys()))
    assert repo.get_commits_count() == expected_commit_counts

    # Test Language Detection
    expected_languages = {
        "TypeScript": 1,
        "Python": 1,
        "Others": 1,
    }
    assert repo.get_language_dict() == expected_languages

# Tests that it handles exceptions properly and clears data so no info gets 'cross-contaminated'
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_repository_extrapolate_handles_exception(mock_repo_class):

    # Mock an exception during call
    mock_repo_instance = MagicMock()
    mock_repo_instance.traverse_commits.side_effect = Exception("Simulated Git error")
    mock_repo_class.return_value = mock_repo_instance

    repo = Repository("/mock/path")

    repo.authors = {"Test": ["hash"]}
    repo.language = {"C++": 1}
    
    repo.extrapolate()
    
    # Check that data was cleared upon exception
    assert repo.authors == {}
    assert repo.language == {}

# Tests methods to get repo data upon initialization (empty)
def test_repository_get_methods_initial():
    repo = Repository("/mock/path")
    assert repo.get_authors() == []
    assert repo.get_commits_count() == {}
    assert repo.get_language_dict() == {}

# Tests language detection of files with a known extension
def test_detect_language_known_extensions():
    assert detect_language("script.py") == "Python"
    assert detect_language("/src/index.js") == "JavaScript"
    assert detect_language("header.HPP") == "C++ Header"
    assert detect_language("styles.css") == "CSS"
    assert detect_language("server.go") == "Go"
    
# Tests language detection of files with an unknown extenstion
def test_detect_language_unknown_extension():
    assert detect_language("document.docx") == "Other"
    assert detect_language("archive.zip") == "Other"

# Tests language detection of files with no extensiom
def test_detect_language_no_extension():
    assert detect_language("README") == "Other"
    assert detect_language(".gitignore") == "Other"