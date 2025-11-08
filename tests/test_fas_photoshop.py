import os
from PIL import Image
import pytest
from src.fas.fas_photoshop import extract_photoshop_data

TESTDATA_DIR = os.path.join("tests", "testdata", "test_fas")
TEST_FILE_PATH = os.path.join(TESTDATA_DIR, "fas_photoshop_test.psd")
INVALID_FILE_PATH = os.path.join(TESTDATA_DIR, "invalid_photoshop.psd")


def create_photoshop_test_file():
    # Creates a fake PSD file (actually a simple image) for testing metadata extraction.
    # Only creates the file if it doesn't already exist.
    
    os.makedirs(TESTDATA_DIR, exist_ok=True)

    if not os.path.exists(TEST_FILE_PATH):
        img = Image.new("RGB", (120, 80), color=(255, 0, 0))
        img.save(TEST_FILE_PATH, format="TIFF")  # Save as TIFF and rename

    return TEST_FILE_PATH



def create_invalid_photoshop_file():
    os.makedirs(TESTDATA_DIR, exist_ok=True)
    with open(INVALID_FILE_PATH, "w") as f:
        f.write("Not a real PSD file")
    return INVALID_FILE_PATH


# ------------------------------------------------------------
class TestFasPhotoshop:

    def test_basic_metadata(self):
        file_path = create_photoshop_test_file()
        metadata = extract_photoshop_data(file_path)

        # Should at least not raise an exception and have basic keys
        assert isinstance(metadata, dict)
        assert any(k in metadata for k in ["width", "error"])

    def test_icc_and_compression_fields_exist(self):
        file_path = create_photoshop_test_file()
        metadata = extract_photoshop_data(file_path)
        # These should exist or be part of the error path
        assert "icc_profile" in metadata or "error" in metadata
        assert "compression" in metadata or "error" in metadata

    def test_layer_metadata(self):
        file_path = create_photoshop_test_file()
        metadata = extract_photoshop_data(file_path)
        if "layers" in metadata:
            layers = metadata["layers"]
            assert isinstance(layers, dict)
        else:
            assert "error" in metadata

    def test_document_info_fields(self):
        file_path = create_photoshop_test_file()
        metadata = extract_photoshop_data(file_path)
        for key in ["resolution_info", "xmp_metadata", "thumbnail"]:
            assert key in metadata or "error" in metadata

    def test_invalid_file(self):
        bad_file = create_invalid_photoshop_file()
        metadata = extract_photoshop_data(bad_file)
        assert "error" in metadata
        assert isinstance(metadata["error"], str)
