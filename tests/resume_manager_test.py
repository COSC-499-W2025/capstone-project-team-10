import pytest
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from src.resume.resume_manager import ResumeManager
import src.param.param as param

class TestResumeManager:
    
    @pytest.fixture
    def manager(self, tmp_path, monkeypatch):
        # initialize temporary directory
        # override the internal storage path to use pytest's temp folder
        monkeypatch.setattr(param, "internal_resume_storage_path", str(tmp_path))
        
        # create a dummy source file to use for testing 'create'
        self.source_file = tmp_path / "dummy_resume.pdf"
        self.source_file.write_text("fake pdf content")
        
        # initialize the manager (this triggers _ensure_storage)
        return ResumeManager()

    def test_initialization_creates_index(self, manager, tmp_path):
        """Test that initializing the manager creates the storage folder and index.json."""
        index_path = tmp_path / "index.json"
        
        assert index_path.exists()
        
        with open(index_path, 'r') as f:
            data = json.load(f)
            assert data["next_id"] == 1
            assert data["resumes"] == {}

    def test_create_resume(self, manager, tmp_path):
        """Test creating a resume copies the file and updates the index."""
        resume_id = manager.create(self.source_file, {"project": "Test Project"})
        
        assert resume_id == 1
        
        # Check if file was actually copied to the internal name
        expected_file = tmp_path / "resume_1.pdf"
        assert expected_file.exists()
        
        # Check if index was updated
        index_path = tmp_path / "index.json"
        with open(index_path, 'r') as f:
            data = json.load(f)
            assert data["next_id"] == 2
            assert str(resume_id) in data["resumes"]
            assert data["resumes"]["1"]["metadata"]["project"] == "Test Project"

    def test_get_resume(self, manager, tmp_path):
        """Test retrieving a resume path by ID."""
        # Setup: Create a resume first
        resume_id = manager.create(self.source_file)
        
        retrieved_path = manager.get(resume_id)
        
        assert retrieved_path is not None
        assert retrieved_path.name == f"resume_{resume_id}.pdf"
        assert retrieved_path.exists()
        
        # Test getting a non-existent resume
        assert manager.get(999) is None

    def test_get_all_resumes_sorted(self, manager):
        """Test listing resumes and sorting them by date."""
        # Setup: Create 3 resumes
        id1 = manager.create(self.source_file, {"name": "First"})
        id2 = manager.create(self.source_file, {"name": "Second"})
        id3 = manager.create(self.source_file, {"name": "Third"})
        
        # Manually manipulate timestamps in index.json to ensure distinct times
        index_path = Path(param.internal_resume_storage_path) / "index.json"
        with open(index_path, 'r+') as f:
            data = json.load(f)
            # Make ID 1 the oldest, ID 3 the newest
            data["resumes"][str(id1)]["created_at"] = (datetime.now() - timedelta(hours=2)).isoformat()
            data["resumes"][str(id2)]["created_at"] = (datetime.now() - timedelta(hours=1)).isoformat()
            data["resumes"][str(id3)]["created_at"] = datetime.now().isoformat()
            f.seek(0)
            json.dump(data, f)
            f.truncate()

        # Get all sorted by date (newest first)
        results = manager.get_all(sort_by='date', reverse=True)
        
        assert len(results) == 3
        assert results[0]['id'] == id3  # Newest
        assert results[1]['id'] == id2
        assert results[2]['id'] == id1  # Oldest

    def test_delete_resume(self, manager, tmp_path):
        """Test deleting a resume removes the file and index entry."""
        # Setup
        resume_id = manager.create(self.source_file)
        stored_path = tmp_path / f"resume_{resume_id}.pdf"
        assert stored_path.exists()
        
        success = manager.delete(resume_id)
        
        assert success is True
        assert not stored_path.exists()  # File should be gone
        
        index_path = tmp_path / "index.json"
        with open(index_path, 'r') as f:
            data = json.load(f)
            assert str(resume_id) not in data["resumes"]

    def test_delete_non_existent(self, manager):
        """Test deleting a resume that doesn't exist returns False."""
        assert manager.delete(999) is False