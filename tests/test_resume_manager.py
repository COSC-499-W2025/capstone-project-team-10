import pytest
import json
from src.resume.resume_manager import ResumeManager
import src.param.param as param

class TestResumeManager:
    
    @pytest.fixture
    def manager(self, tmp_path, monkeypatch):
        # initialize temporary directory
        # override the internal storage path to use pytest's temp folder
        monkeypatch.setattr(param, "program_file_path", str(tmp_path))
        
        # create a dummy source file to use for testing 'create'
        self.source_file = tmp_path / "dummy_resume.pdf"
        self.source_file.write_text("fake pdf content")
        
        # initialize the manager (this triggers _ensure_storage)
        return ResumeManager()

    def test_initialization_creates_index(self, manager, tmp_path):
        """Test that initializing the manager creates the storage folder and index.json."""
        storage_dir = tmp_path / "storage" / "resumes"
        index_path = storage_dir / "index.json"
        
        manager._ensure_storage()
        
        assert storage_dir.exists()
        assert index_path.exists()
        
        with open(index_path, 'r') as f:
            data = json.load(f)
            assert data["next_id"] == 1
            assert data["resumes"] == {}

    def test_create_resume(self, manager, tmp_path):
        """Test creating a resume copies the file and updates the index."""
        resume_id = manager.create(
            self.source_file,
            {"type": "pdf_resume", "source_log": "C:/tmp/example.log"},
        )
        
        assert resume_id == 1
        
        # Check if file was actually copied to the internal name
        storage_dir = tmp_path / "storage" / "resumes"
        expected_file = storage_dir / "resume_1.pdf"
        assert expected_file.exists()
        
        # Check if index was updated
        index_path = storage_dir / "index.json"
        with open(index_path, 'r') as f:
            data = json.load(f)
            assert data["next_id"] == 2
            assert str(resume_id) in data["resumes"]
            entry = data["resumes"]["1"]
            assert entry["id"] == 1
            assert entry["type"] == "pdf_resume"
            assert entry["source_log"] == "C:/tmp/example.log"
            assert entry["original"]["name"] == self.source_file.name
            assert entry["backup"]["name"] == "resume_1.pdf"
            assert entry["created_date"] != ""

    def test_get_resume(self, manager, tmp_path):
        """Test retrieving a resume path by ID."""
        # Setup: Create a resume first
        resume_id = manager.create(self.source_file)
        
        retrieved_path = manager.get(resume_id)
        
        assert retrieved_path is not None
        assert retrieved_path.name == f"resume_{resume_id}.pdf"
        assert str(tmp_path) in str(retrieved_path)
        
        # Test getting a non-existent resume
        assert manager.get(999) is None

    def test_get_all_resumes_sorted(self, manager):
        """Test listing resumes and sorting them by id."""
        # Setup: Create 3 resumes
        id1 = manager.create(self.source_file, {"name": "First"})
        id2 = manager.create(self.source_file, {"name": "Second"})
        results = manager.get_all(sort_by='id', reverse=True)
        
        # Assertions
        assert len(results) == 2
        assert results[0]['id'] == id2
        assert results[1]['id'] == id1

    def test_delete_resume(self, manager, tmp_path):
        """Test deleting a resume removes the file and index entry."""
        # Setup
        resume_id = manager.create(self.source_file)
        storage_dir = tmp_path / "storage" / "resumes"
        stored_path = storage_dir / f"resume_{resume_id}.pdf"
        assert stored_path.exists()
        
        success = manager.delete(resume_id)
        
        assert success is True
        assert not stored_path.exists()  # File should be gone
        
        index_path = storage_dir / "index.json"
        with open(index_path, 'r') as f:
            data = json.load(f)
            assert str(resume_id) not in data["resumes"]

    def test_delete_non_existent(self, manager):
        """Test deleting a resume that doesn't exist returns False."""
        assert manager.delete(999) is False