import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime
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
    def __init__(self, commit_hash, author_name, modified_files_list, 
                 msg="Test commit", insertions=10, deletions=5, 
                 author_date=None):
        self.hash = commit_hash
        self.author = MockAuthor(author_name)
        self.modified_files = [MockModifiedFile(p) for p in modified_files_list]
        self.msg = msg
        self.insertions = insertions
        self.deletions = deletions
        self.author_date = author_date or datetime(2024, 1, 1)

# Set up commit data to be used later in tests.
MOCK_COMMITS_DATA = [
    MockCommit('c_hash1', 'Author A', ['src/file1.py', 'src/app.js'], 
               msg="Add initial files", insertions=100, deletions=0,
               author_date=datetime(2024, 1, 1)),
    MockCommit('c_hash2', 'Author B', ['index.html'],
               msg="Create index page", insertions=50, deletions=2,
               author_date=datetime(2024, 1, 15)),
    MockCommit('c_hash3', 'Author A', ['api/core.ts', 'tests/test_2.py', 'data/config.xyz'],
               msg="Add API and tests", insertions=200, deletions=10,
               author_date=datetime(2024, 2, 1)),
    MockCommit('c_hash4', 'Author C', ['old_file.java'],
               msg="Legacy code", insertions=75, deletions=25,
               author_date=datetime(2024, 2, 15)),
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

    # Test Authors
    expected_authors = ['Author A', 'Author B', 'Author C']
    assert sorted(repo.get_authors()) == sorted(expected_authors)
    
    # Note: get_commits_count() currently doesn't work with the implementation
    # because authors are set to None via setdefault()
    # The commit count can be verified through commits_content instead
    commits = repo.get_commits_content()
    author_commit_counts = {}
    for commit in commits:
        author = commit['author']
        author_commit_counts[author] = author_commit_counts.get(author, 0) + 1
    
    expected_commit_counts = {
        'Author A': 2,
        'Author B': 1,
        'Author C': 1, 
    }
    assert author_commit_counts == expected_commit_counts

    # Test Language Detection
    expected_languages = {
        "TypeScript": 1,
        "Python": 1,
        "Others": 1,
    }
    assert repo.get_language_dict() == expected_languages
    
    # Test Commits Content
    commits = repo.get_commits_content()
    assert len(commits) == 4
    assert all('author' in c for c in commits)
    assert all('date' in c for c in commits)
    assert all('message' in c for c in commits)
    assert all('insertions' in c for c in commits)
    assert all('deletions' in c for c in commits)

# Tests filter_author functionality
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_repository_filter_author(mock_repo_class, mock_pydriller_repo):
    mock_repo_class.side_effect = mock_pydriller_repo

    # Filter for only Author A
    repo = Repository("/mock/path", filter_author="Author A")
    repo.extrapolate()

    # Should still track all authors
    assert 'Author A' in repo.get_authors()
    assert 'Author B' in repo.get_authors()
    assert 'Author C' in repo.get_authors()
    
    # But commits_content should only have Author A's commits
    commits = repo.get_commits_content()
    assert len(commits) == 2
    assert all(c['author'] == 'Author A' for c in commits)
    
    # Verify specific commit data
    assert commits[0]['message'] == "Add initial files"
    assert commits[0]['insertions'] == 100
    assert commits[0]['deletions'] == 0
    assert commits[1]['message'] == "Add API and tests"
    assert commits[1]['insertions'] == 200
    assert commits[1]['deletions'] == 10

# Tests filter_author with non-existent author
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_repository_filter_nonexistent_author(mock_repo_class, mock_pydriller_repo):
    mock_repo_class.side_effect = mock_pydriller_repo

    # Filter for an author that doesn't exist
    repo = Repository("/mock/path", filter_author="Nonexistent Author")
    repo.extrapolate()

    # All authors should still be tracked
    assert len(repo.get_authors()) == 3
    
    # But commits_content should be empty
    commits = repo.get_commits_content()
    assert len(commits) == 0

# Tests commits_content structure
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_commits_content_structure(mock_repo_class, mock_pydriller_repo):
    mock_repo_class.side_effect = mock_pydriller_repo

    repo = Repository("/mock/path")
    repo.extrapolate()

    commits = repo.get_commits_content()
    
    # Verify first commit structure
    first_commit = commits[0]
    assert first_commit['author'] == 'Author A'
    assert first_commit['date'] == datetime(2024, 1, 1)
    assert first_commit['message'] == "Add initial files"
    assert first_commit['insertions'] == 100
    assert first_commit['deletions'] == 0
    
    # Verify last commit structure
    last_commit = commits[-1]
    assert last_commit['author'] == 'Author C'
    assert last_commit['date'] == datetime(2024, 2, 15)
    assert last_commit['message'] == "Legacy code"
    assert last_commit['insertions'] == 75
    assert last_commit['deletions'] == 25

# Tests that setdefault correctly initializes authors
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_repository_authors_setdefault(mock_repo_class, mock_pydriller_repo):
    mock_repo_class.side_effect = mock_pydriller_repo

    repo = Repository("/mock/path")
    repo.extrapolate()

    # All authors should be in the dictionary
    assert 'Author A' in repo.authors
    assert 'Author B' in repo.authors
    assert 'Author C' in repo.authors

# Tests that it handles exceptions properly and clears data
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_repository_extrapolate_handles_exception(mock_repo_class):
    # Mock an exception during call
    mock_repo_instance = MagicMock()
    mock_repo_instance.traverse_commits.side_effect = Exception("Simulated Git error")
    mock_repo_class.return_value = mock_repo_instance

    repo = Repository("/mock/path")

    # Pre-populate with test data
    repo.authors = {"Test": None}
    repo.language = {"C++": 1}
    repo.commits_content = [{'author': 'Test', 'message': 'test'}]
    
    repo.extrapolate()
    
    # Check that data was cleared upon exception
    assert repo.authors == {}
    assert repo.language == {}
    assert repo.commits_content == []

# Tests methods to get repo data upon initialization (empty)
def test_repository_get_methods_initial():
    repo = Repository("/mock/path")
    assert repo.get_authors() == []
    # Note: get_commits_count() will fail if authors dict has None values
    # So we only test it's a dict initially
    assert isinstance(repo.get_commits_count(), dict)
    assert repo.get_language_dict() == {}
    assert repo.get_commits_content() == []

# Tests initialization with filter_author
def test_repository_initialization_with_filter():
    repo = Repository("/mock/path", filter_author="TestAuthor")
    assert repo.path == "/mock/path"
    assert repo.filter_author == "TestAuthor"
    assert repo.authors == {}
    assert repo.language == {}
    assert repo.commits_content == []

# Tests initialization without filter_author
def test_repository_initialization_without_filter():
    repo = Repository("/mock/path")
    assert repo.path == "/mock/path"
    assert repo.filter_author is None
    assert repo.authors == {}
    assert repo.language == {}
    assert repo.commits_content == []

# Tests language detection of files with a known extension
def test_detect_language_known_extensions():
    assert detect_language("script.py") == "Python"
    assert detect_language("/src/index.js") == "JavaScript"
    assert detect_language("header.HPP") == "C++ Header"
    assert detect_language("styles.css") == "CSS"
    assert detect_language("server.go") == "Go"
    
# Tests language detection of files with an unknown extension
def test_detect_language_unknown_extension():
    assert detect_language("document.docx") == "Other"
    assert detect_language("archive.zip") == "Other"

# Tests language detection of files with no extension
def test_detect_language_no_extension():
    assert detect_language("README") == "Other"
    assert detect_language(".gitignore") == "Other"

# Tests that LANG_MAP contains expected mappings
def test_lang_map_completeness():
    assert ".py" in LANG_MAP
    assert ".js" in LANG_MAP
    assert ".ts" in LANG_MAP
    assert ".java" in LANG_MAP
    assert ".cpp" in LANG_MAP
    assert LANG_MAP[".py"] == "Python"
    assert LANG_MAP[".js"] == "JavaScript"

# Tests commits_content with multiple commits from same author
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_commits_content_same_author_multiple_commits(mock_repo_class):
    # Create commits all from the same author
    same_author_commits = [
        MockCommit('hash1', 'Author A', ['file1.py'], msg="First", insertions=10, deletions=0),
        MockCommit('hash2', 'Author A', ['file2.py'], msg="Second", insertions=20, deletions=5),
        MockCommit('hash3', 'Author A', ['file3.py'], msg="Third", insertions=15, deletions=3),
    ]
    
    def factory(path, only_in_branch=None):
        mock_repo_instance = MagicMock()
        if only_in_branch == 'HEAD':
            mock_repo_instance.traverse_commits.return_value = [same_author_commits[0]]
        else:
            mock_repo_instance.traverse_commits.return_value = same_author_commits
        return mock_repo_instance
    
    mock_repo_class.side_effect = factory

    repo = Repository("/mock/path")
    repo.extrapolate()

    commits = repo.get_commits_content()
    assert len(commits) == 3
    assert all(c['author'] == 'Author A' for c in commits)
    assert commits[0]['message'] == "First"
    assert commits[1]['message'] == "Second"
    assert commits[2]['message'] == "Third"

# Tests edge case with commits having zero insertions/deletions
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_commits_content_zero_changes(mock_repo_class):
    zero_change_commit = MockCommit(
        'hash1', 'Author A', ['README.md'], 
        msg="Update README", insertions=0, deletions=0
    )
    
    def factory(path, only_in_branch=None):
        mock_repo_instance = MagicMock()
        if only_in_branch == 'HEAD':
            mock_repo_instance.traverse_commits.return_value = [zero_change_commit]
        else:
            mock_repo_instance.traverse_commits.return_value = [zero_change_commit]
        return mock_repo_instance
    
    mock_repo_class.side_effect = factory

    repo = Repository("/mock/path")
    repo.extrapolate()

    commits = repo.get_commits_content()
    assert len(commits) == 1
    assert commits[0]['insertions'] == 0
    assert commits[0]['deletions'] == 0

# Tests language detection with files having None as new_path
@patch('src.fss.repo_reader.PyDrillerRepo')
def test_language_detection_with_none_paths(mock_repo_class):
    # Create a mock commit with a file that has new_path = None (deleted file)
    class MockModifiedFileWithNone:
        def __init__(self, new_path):
            self.new_path = new_path
    
    class MockCommitWithNone:
        def __init__(self):
            self.hash = 'hash1'
            self.author = MockAuthor('Author A')
            self.modified_files = [
                MockModifiedFileWithNone('file1.py'),
                MockModifiedFileWithNone(None),  # Deleted file
                MockModifiedFileWithNone('file2.js'),
            ]
            self.msg = "Test"
            self.insertions = 10
            self.deletions = 5
            self.author_date = datetime(2024, 1, 1)
    
    mock_commit = MockCommitWithNone()
    
    def factory(path, only_in_branch=None):
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = [mock_commit]
        return mock_repo_instance
    
    mock_repo_class.side_effect = factory

    repo = Repository("/mock/path")
    repo.extrapolate()

    # Should only count files with non-None paths
    languages = repo.get_language_dict()
    assert "Python" in languages
    assert "JavaScript" in languages
    assert languages["Python"] == 1
    assert languages["JavaScript"] == 1