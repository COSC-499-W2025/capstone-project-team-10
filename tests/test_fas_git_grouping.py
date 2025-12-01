import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path
from datetime import datetime
from src.fas.fas_git_grouping import GitGrouping

# Test data used for mocks and assertions
MOCK_REPO_PATH = "/unresolved/path/to/repo"
MOCK_RESOLVED_PATH_STR = str(Path("/resolved/path/to/repo"))
MOCK_RESOLVED_PATH_OBJ = Path(MOCK_RESOLVED_PATH_STR) 
MOCK_CUSTOM_ID = "CustomRepoID"
MOCK_GIT_FILES_RAW = ["file1.py", " file2.js ", "", "  \n", "docs/README.md", "a-file-with-no-ext"]
EXPECTED_FILES = ["file1.py", "file2.js", "docs/README.md", "a-file-with-no-ext"]
MOCK_CREATED_DATE = datetime(2024, 1, 1, 12, 0, 0)
MOCK_MODIFIED_DATE = datetime(2024, 11, 30, 18, 0, 0)
MOCK_AUTHORS = ["author1@example.com", "author2@example.com"]

# Mock commit data
MOCK_COMMITS = [
    {"message": "Fix critical bug in login", "insertions": 10, "deletions": 5},
    {"message": "Add new feature for user dashboard", "insertions": 50, "deletions": 2},
    {"message": "Update README documentation", "insertions": 15, "deletions": 3},
    {"message": "Refactor database connection", "insertions": 30, "deletions": 25},
    {"message": "Add test coverage for API", "insertions": 40, "deletions": 0},
]

# Mock file analysis result
MOCK_FILE_RESULT = MagicMock()
MOCK_FILE_RESULT.file_name = "test_file.py"
MOCK_FILE_RESULT.file_type = "Python"
MOCK_FILE_RESULT.last_modified = datetime(2024, 11, 1)
MOCK_FILE_RESULT.created_time = datetime(2024, 1, 15)
MOCK_FILE_RESULT.extra_data = {"lines": 100}

# Mocks the Path calls
@pytest.fixture
def mock_path_resolve():
    with patch('src.fas.fas_git_grouping.Path') as MockPath:
        path_instance_mock = MagicMock()
        path_instance_mock.resolve.return_value = MOCK_RESOLVED_PATH_OBJ
        MockPath.return_value = path_instance_mock
        yield MockPath

# Mocks the repo_reader
@pytest.fixture
def mock_repository_class():
    MockRepo = MagicMock()
    MockRepo.return_value.extrapolate.return_value = None
    MockRepo.return_value.get_authors.return_value = MOCK_AUTHORS
    MockRepo.return_value.get_commits_content.return_value = MOCK_COMMITS
    return MockRepo

# Mocks pydriller.Git
@pytest.fixture
def mock_git_class():
    MockGit = MagicMock()
    MockGit.return_value.files.return_value = MOCK_GIT_FILES_RAW
    return MockGit

# Mocks PyDrillerRepo for date extraction
@pytest.fixture
def mock_pydriller_repo():
    with patch('src.fas.fas_git_grouping.PyDrillerRepo') as MockPyDrillerRepo:
        mock_commit_1 = MagicMock()
        mock_commit_1.committer_date = MOCK_MODIFIED_DATE
        mock_commit_2 = MagicMock()
        mock_commit_2.committer_date = MOCK_CREATED_DATE
        
        MockPyDrillerRepo.return_value.traverse_commits.return_value = [
            mock_commit_1,
            mock_commit_2
        ]
        yield MockPyDrillerRepo

# Mock param module
@pytest.fixture
def mock_param():
    with patch('src.fas.fas_git_grouping.param') as mock_param:
        mock_param.get.return_value = "test_user"
        yield mock_param

# Mock fas module
@pytest.fixture
def mock_fas():
    with patch('src.fas.fas_git_grouping.fas') as mock_fas:
        mock_fas.run_fas.return_value = MOCK_FILE_RESULT
        yield mock_fas

# Mock os functions
@pytest.fixture
def mock_os():
    with patch('src.fas.fas_git_grouping.os') as mock_os:
        mock_os.path.join = lambda *args: "/".join(args)
        mock_os.path.isfile.return_value = True
        yield mock_os

# Test add_repository with complete git_output structure
@patch('src.fas.fas_git_grouping.Git')
@patch('src.fas.fas_git_grouping.PyDrillerRepo')
@patch('src.fas.fas_git_grouping.Repository')
@patch('src.fas.fas_git_grouping.param')
@patch('src.fas.fas_git_grouping.fas')
@patch('src.fas.fas_git_grouping.os')
def test_add_repository_complete_output(mock_os, mock_fas, mock_param, mock_repo_class, mock_pydriller_repo, mock_git_class, mock_path_resolve):
    # Setup mocks
    mock_param.get.return_value = "test_user"
    mock_git_class.return_value.files.return_value = MOCK_GIT_FILES_RAW
    mock_repo_class.return_value.get_authors.return_value = MOCK_AUTHORS
    mock_repo_class.return_value.get_commits_content.return_value = MOCK_COMMITS
    mock_fas.run_fas.return_value = MOCK_FILE_RESULT
    mock_os.path.join = lambda *args: "/".join(args)
    mock_os.path.isfile.return_value = True
    
    # Setup PyDrillerRepo for dates
    mock_commit_1 = MagicMock()
    mock_commit_1.committer_date = MOCK_MODIFIED_DATE
    mock_commit_2 = MagicMock()
    mock_commit_2.committer_date = MOCK_CREATED_DATE
    mock_pydriller_repo.return_value.traverse_commits.return_value = [mock_commit_1, mock_commit_2]

    grouping = GitGrouping()
    git_output = grouping.add_repository(MOCK_REPO_PATH)
    
    # Verify git_output structure
    assert "author" in git_output
    assert "title" in git_output
    assert "subject" in git_output
    assert "created" in git_output
    assert "modified" in git_output
    assert "extra data" in git_output
    assert "commits" in git_output
    
    # Verify git_output values
    assert git_output["author"] == MOCK_AUTHORS
    assert git_output["title"] == MOCK_RESOLVED_PATH_STR
    assert git_output["subject"] == "Git Repo"
    assert git_output["created"] == MOCK_CREATED_DATE
    assert git_output["modified"] == MOCK_MODIFIED_DATE
    
    # Verify commits analysis
    assert git_output["commits"]["total_commits"] == 5
    assert git_output["commits"]["total_insertions"] == 145
    assert git_output["commits"]["total_deletions"] == 35
    assert git_output["commits"]["net_change"] == 110

# Test add_repository with custom ID
@patch('src.fas.fas_git_grouping.Git')
@patch('src.fas.fas_git_grouping.PyDrillerRepo')
@patch('src.fas.fas_git_grouping.Repository')
@patch('src.fas.fas_git_grouping.param')
@patch('src.fas.fas_git_grouping.fas')
@patch('src.fas.fas_git_grouping.os')
def test_add_repository_custom_id(mock_os, mock_fas, mock_param, mock_repo_class, mock_pydriller_repo, mock_git_class, mock_path_resolve):
    # Setup basic mocks
    mock_param.get.return_value = "test_user"
    mock_git_class.return_value.files.return_value = []
    mock_repo_class.return_value.get_commits_content.return_value = []
    mock_fas.run_fas.return_value = None
    mock_os.path.isfile.return_value = False
    mock_pydriller_repo.return_value.traverse_commits.return_value = []

    grouping = GitGrouping()
    git_output = grouping.add_repository(MOCK_REPO_PATH, repo_id=MOCK_CUSTOM_ID)
    
    assert git_output["title"] == MOCK_CUSTOM_ID
    assert MOCK_CUSTOM_ID in grouping.repositories
    assert MOCK_CUSTOM_ID in grouping.files
    assert MOCK_CUSTOM_ID in grouping.commits
    assert MOCK_RESOLVED_PATH_STR not in grouping.repositories

# Test get_repo_files with file analysis
@patch('src.fas.fas_git_grouping.Git')
@patch('src.fas.fas_git_grouping.fas')
@patch('src.fas.fas_git_grouping.os')
def test_get_repo_files_with_analysis(mock_os, mock_fas, mock_git_class):
    mock_git_class.return_value.files.return_value = ["test_file.py"]
    mock_fas.run_fas.return_value = MOCK_FILE_RESULT
    mock_os.path.join = lambda *args: "/".join(args)
    mock_os.path.isfile.return_value = True
    
    grouping = GitGrouping()
    files = grouping.get_repo_files(MOCK_RESOLVED_PATH_STR, "test_id")
    
    assert len(files) == 1
    assert files[0]["File name"] == "test_file.py"
    assert files[0]["File type"] == "Python"
    assert files[0]["Last modified"] == MOCK_FILE_RESULT.last_modified
    assert files[0]["Created time"] == MOCK_FILE_RESULT.created_time
    assert files[0]["Extra data"] == {"lines": 100}

# Test get_repo_files filtering
@patch('src.fas.fas_git_grouping.Git')
@patch('src.fas.fas_git_grouping.fas')
@patch('src.fas.fas_git_grouping.os')
def test_get_repo_files_filters_correctly(mock_os, mock_fas, mock_git_class):
    mock_git_class.return_value.files.return_value = MOCK_GIT_FILES_RAW
    mock_fas.run_fas.return_value = MOCK_FILE_RESULT
    mock_os.path.join = lambda *args: "/".join(args)
    mock_os.path.isfile.return_value = True
    
    grouping = GitGrouping()
    files = grouping.get_repo_files(MOCK_RESOLVED_PATH_STR, "test_id")
    
    assert len(files) == 4

# Test get_repo_files with .git suffix removal
@patch('src.fas.fas_git_grouping.Git')
@patch('src.fas.fas_git_grouping.fas')
@patch('src.fas.fas_git_grouping.os')
def test_get_repo_files_removes_git_suffix(mock_os, mock_fas, mock_git_class):
    mock_git_class.return_value.files.return_value = []
    mock_fas.run_fas.return_value = None
    mock_os.path.isfile.return_value = False
    
    grouping = GitGrouping()
    grouping.get_repo_files("/path/to/repo.git", "test_id")
    
    mock_git_class.assert_called_once_with("/path/to/repo")

# Test get_repo_files exception handling
@patch('src.fas.fas_git_grouping.Git')
def test_get_repo_files_git_exception(mock_git_class):
    mock_git_class.return_value.files.side_effect = RuntimeError("Git command failed")
    
    grouping = GitGrouping()
    files = grouping.get_repo_files("/any/path", "test_id")
    
    assert files == set()

# Test get_repo_dates success
@patch('src.fas.fas_git_grouping.PyDrillerRepo')
def test_get_repo_dates_success(mock_pydriller_repo):
    mock_commit_1 = MagicMock()
    mock_commit_1.committer_date = MOCK_MODIFIED_DATE
    mock_commit_2 = MagicMock()
    mock_commit_2.committer_date = MOCK_CREATED_DATE
    
    mock_pydriller_repo.return_value.traverse_commits.return_value = [
        mock_commit_1,
        mock_commit_2
    ]
    
    grouping = GitGrouping()
    created, modified = grouping.get_repo_dates(MOCK_RESOLVED_PATH_STR)
    
    assert created == MOCK_CREATED_DATE
    assert modified == MOCK_MODIFIED_DATE

# Test get_repo_dates with no commits
@patch('src.fas.fas_git_grouping.PyDrillerRepo')
def test_get_repo_dates_no_commits(mock_pydriller_repo):
    mock_pydriller_repo.return_value.traverse_commits.return_value = []
    
    grouping = GitGrouping()
    created, modified = grouping.get_repo_dates(MOCK_RESOLVED_PATH_STR)
    
    assert created is None
    assert modified is None

# Test get_repo_dates exception handling
@patch('src.fas.fas_git_grouping.PyDrillerRepo')
def test_get_repo_dates_exception(mock_pydriller_repo):
    mock_pydriller_repo.side_effect = Exception("PyDriller error")
    
    grouping = GitGrouping()
    created, modified = grouping.get_repo_dates(MOCK_RESOLVED_PATH_STR)
    
    assert created is None
    assert modified is None

# Test commit_analysis with valid data
def test_commit_analysis():
    grouping = GitGrouping()
    result = grouping.commit_analysis(MOCK_COMMITS)
    
    assert result["total_commits"] == 5
    assert result["total_insertions"] == 145
    assert result["total_deletions"] == 35
    assert result["net_change"] == 110
    assert "message_analysis" in result

# Test commit_analysis with empty commits
def test_commit_analysis_empty():
    grouping = GitGrouping()
    result = grouping.commit_analysis([])
    
    assert result["total_commits"] == 0
    assert result["total_insertions"] == 0
    assert result["total_deletions"] == 0
    assert result["message_analysis"] == {}

# Test commit_analysis with None
def test_commit_analysis_none():
    grouping = GitGrouping()
    result = grouping.commit_analysis(None)
    
    assert result["total_commits"] == 0
    assert result["total_insertions"] == 0
    assert result["total_deletions"] == 0

# Test _categorize_messages
def test_categorize_messages():
    grouping = GitGrouping()
    messages = [
        "Fix critical bug in login",
        "Add new feature for user dashboard",
        "Update README documentation",
        "Refactor database connection",
        "Add test coverage for API",
        "Format code with black",
        "Random commit message"
    ]
    
    categories = grouping._categorize_messages(messages)
    
    assert "fix" in categories
    assert "feature" in categories
    assert "docs" in categories
    assert "refactor" in categories
    assert "style" in categories
    assert "other" in categories

# Test _categorize_messages with empty list
def test_categorize_messages_empty():
    grouping = GitGrouping()
    categories = grouping._categorize_messages([])
    
    assert categories == set()

# Test _categorize_messages with mixed case
def test_categorize_messages_case_insensitive():
    grouping = GitGrouping()
    messages = [
        "FIX BUG",
        "Add Feature",
        "update docs"
    ]
    
    categories = grouping._categorize_messages(messages)
    
    assert "fix" in categories
    assert "feature" in categories
    assert "docs" in categories

# Test GitGrouping initial state
def test_git_grouping_initial_state():
    grouping = GitGrouping()
    assert grouping.repositories == {}
    assert grouping.files == {}
    assert grouping.commits == {}

# Test multiple repository additions
@patch('src.fas.fas_git_grouping.Git')
@patch('src.fas.fas_git_grouping.PyDrillerRepo')
@patch('src.fas.fas_git_grouping.Repository')
@patch('src.fas.fas_git_grouping.param')
@patch('src.fas.fas_git_grouping.fas')
@patch('src.fas.fas_git_grouping.os')
def test_multiple_repositories(mock_os, mock_fas, mock_param, mock_repo_class,mock_pydriller_repo, mock_git_class, mock_path_resolve):
    # Setup basic mocks
    mock_param.get.return_value = "test_user"
    mock_git_class.return_value.files.return_value = []
    mock_repo_class.return_value.get_commits_content.return_value = []
    mock_fas.run_fas.return_value = None
    mock_os.path.isfile.return_value = False
    mock_pydriller_repo.return_value.traverse_commits.return_value = []
    
    grouping = GitGrouping()
    grouping.add_repository(MOCK_REPO_PATH, repo_id="repo1")
    grouping.add_repository(MOCK_REPO_PATH, repo_id="repo2")
    
    assert len(grouping.repositories) == 2
    assert len(grouping.files) == 2
    assert len(grouping.commits) == 2
    assert "repo1" in grouping.repositories
    assert "repo2" in grouping.repositories