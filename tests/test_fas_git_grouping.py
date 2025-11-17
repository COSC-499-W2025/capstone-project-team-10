import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.fas.fas_git_grouping import GitGrouping

# Test data used for mocks and assertions
MOCK_REPO_PATH = "/unresolved/path/to/repo"
MOCK_RESOLVED_PATH_STR = str(Path("/resolved/path/to/repo"))
MOCK_RESOLVED_PATH_OBJ = Path(MOCK_RESOLVED_PATH_STR) 
MOCK_CUSTOM_ID = "CustomRepoID"
MOCK_GIT_FILES_RAW = ["file1.py", " file2.js ", "", "  \n", "docs/README.md", "a-file-with-no-ext"]
EXPECTED_FILES = ["file1.py", "file2.js", "docs/README.md", "a-file-with-no-ext"]

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
    return MockRepo

# Mocks pydriller.Git
@pytest.fixture
def mock_git_class():
    MockGit = MagicMock()
    MockGit.return_value.files.return_value = MOCK_GIT_FILES_RAW
    return MockGit

# Test add_repository in adding the correct data and returning it when accessed via the unique ID (repo path)
@patch('src.fas.fas_git_grouping.Git')
@patch('src.fas.fas_git_grouping.Repository')
def test_add_repository_default_id(mock_repo_class, mock_git_class, mock_path_resolve):
    # Load test data into repo mock
    mock_git_class.return_value.files.return_value = MOCK_GIT_FILES_RAW

    grouping = GitGrouping()
    
    returned_files, returned_id = grouping.add_repository(MOCK_REPO_PATH)
    
    mock_path_resolve.assert_called_with(MOCK_REPO_PATH)

    mock_repo_class.assert_called_once_with(MOCK_RESOLVED_PATH_STR)
    mock_repo_class.return_value.extrapolate.assert_called_once()
    
    mock_git_class.assert_called_once_with(MOCK_RESOLVED_PATH_STR)
    mock_git_class.return_value.files.assert_called_once()
    
    # Assert correct files and unique ID were returned are correct
    assert returned_id == MOCK_RESOLVED_PATH_STR
    assert returned_files == EXPECTED_FILES 

    # Assert that the correct data can be accessed via the unique ID
    assert grouping.repositories[MOCK_RESOLVED_PATH_STR] == mock_repo_class.return_value
    assert grouping.files[MOCK_RESOLVED_PATH_STR] == EXPECTED_FILES

# Test add_repository to give the correct unique ID
@patch('src.fas.fas_git_grouping.Git')
@patch('src.fas.fas_git_grouping.Repository')
def test_add_repository_custom_id(mock_repo_class, mock_git_class, mock_path_resolve):
    # Load test data into repo mock
    mock_git_class.return_value.files.return_value = MOCK_GIT_FILES_RAW

    grouping = GitGrouping()
    
    returned_files, returned_id = grouping.add_repository(MOCK_REPO_PATH, repo_id=MOCK_CUSTOM_ID)
    
    assert returned_id == MOCK_CUSTOM_ID
    assert MOCK_CUSTOM_ID in grouping.repositories
    assert MOCK_RESOLVED_PATH_STR not in grouping.repositories
    assert grouping.files[MOCK_CUSTOM_ID] == EXPECTED_FILES
    mock_repo_class.assert_called_once_with(MOCK_RESOLVED_PATH_STR)

# Test exception handling done by get_repo_files
@patch('src.fas.fas_git_grouping.Git')
def test_get_repo_files_git_exception(mock_git_class):
    #Cause the exception
    mock_git_class.return_value.files.side_effect = RuntimeError("Git command failed")
    
    grouping = GitGrouping()
    
    # Call the function
    files = grouping.get_repo_files("/any/path", "test_id")
    
    # Exception should return an empty set
    assert files == []

# Tests methods to get grouping data upon initialization (empty)
def test_git_grouping_initial_state():
    grouping = GitGrouping()
    assert grouping.repositories == {}
    assert grouping.files == {}