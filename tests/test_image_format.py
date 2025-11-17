from __future__ import annotations
from pathlib import Path
import pytest
from src.fas.fas_image_format import analyze_image

def test_jpeg_metadata():
    image_path = Path("tests/testdata/test_image/happy dreams.jpg")
    result = analyze_image(image_path)
    
    assert result["file"]["size_bytes"] > 0
    assert result["image"]["format"] in ("JPEG", "JPG", "JFIF")
    assert result["image"]["width"] > 0
    assert result["image"]["height"] > 0
    assert isinstance(result["type_specific"], dict)
    assert isinstance(result["warnings"], list)

def test_png_metadata():
    image_path = Path("tests/testdata/test_image/takanaka.png")
    result = analyze_image(image_path)

    assert result["file"]["size_bytes"] > 0
    assert result["image"]["format"] == "PNG"
    assert result["image"]["width"] > 0
    assert result["image"]["height"] > 0

    png_data = result["type_specific"]
    assert "color_type_from_mode" in png_data

def test_gif_metadata():
    image_path = Path("tests/testdata/test_image/ae86.gif")
    result = analyze_image(image_path)

    assert result["file"]["size_bytes"] > 0
    assert result["image"]["format"] == "GIF"
    assert isinstance(result["image"]["is_animated"], bool)
    assert isinstance(result["image"]["frames"], int)

def test_webp_metadata():
    image_path = Path("tests/testdata/test_image/oopsie.webp")
    result = analyze_image(image_path)

    assert result["file"]["size_bytes"] > 0
    assert result["image"]["format"] == "WEBP"
    assert result["image"]["width"] > 0
    assert isinstance(result["type_specific"], dict)

def test_tiff_metadata():
    image_path = Path("tests/testdata/test_image/lebron.tiff")
    result = analyze_image(image_path)

    assert result["file"]["size_bytes"] > 0
    assert result["image"]["format"] == "TIFF"
    assert result["image"]["width"] > 0
    assert result["image"]["height"] > 0
    assert isinstance(result["type_specific"], dict)

def test_invalid_file():
    result = analyze_image(r"poopoo/waawaa/hello/this/is/garbage")

    assert len(result["warnings"]) > 0