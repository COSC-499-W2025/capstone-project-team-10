# image_meta_core.py
from __future__ import annotations
import os
from typing import Any, Dict, Optional
from PIL import Image, ImageFile

#Constants

# Recognized file extensions for optional helpers (kept for future use)
JPEG_FORMATS = {"JPEG", "JPG", "JFIF"}
PNG_FORMATS = {"PNG"}
GIF_FORMATS = {"GIF"}
WEBP_FORMATS = {"WEBP"}
TIFF_FORMATS = {"TIFF"}
BMP_FORMATS = {"BMP", "DIB"}
HEIF_FORMATS = {"HEIF", "HEIC", "AVIF"}

# Mode to bit depth per channel
MODE_TO_BITS: Dict[str, int] = {
    "1": 1,
    "L": 8,
    "P": 8,
    "LA": 8,
    "RGB": 8,
    "RGBA": 8,
    "CMYK": 8,
    "YCbCr": 8,
    "I;16": 16,
    "I;16B": 16,
    "I;16L": 16,
    "I": 32,
    "F": 32,
}

# Common textual keys we’ll pull from PNG when available
PNG_TEXT_KEYS = ("Comment", "Description", "Title", "Author", "Copyright", "Software")


def analyze_image(path: str) -> Dict[str, Any]:
    """
    Analyze an image file and return a JSON-serializable dict with:
      - file basics
      - image basics
      - type_specific (format-dependent items)
      - warnings (non-fatal issues)
    """
    result: Dict[str, Any] = {
        "file": {"path": path, "size_bytes": _file_size(path)},
        "image": {},
        "type_specific": {},
        "warnings": [],
    }

    try:
        image = _safe_open(path)
    except Exception as exc:
        result["warnings"].append(f"Pillow failed to open: {exc!r}")
        return result

    try:
        result["image"] = _basic_image_info(image)
    except Exception as exc:
        result["warnings"].append(f"Failed to get basic image info: {exc!r}")

    # Format-specific extras
    try:
        format_name = (image.format or "").upper()
        if format_name in JPEG_FORMATS:
            result["type_specific"] = extract_jpeg_specific(image)
        elif format_name in PNG_FORMATS:
            result["type_specific"] = extract_png_specific(image)
        elif format_name in GIF_FORMATS:
            result["type_specific"] = extract_gif_specific(image)
        elif format_name in WEBP_FORMATS:
            result["type_specific"] = extract_webp_specific(image)
        elif format_name in TIFF_FORMATS:
            result["type_specific"] = extract_tiff_specific(image)
        elif format_name in BMP_FORMATS:
            result["type_specific"] = extract_bmp_specific(image)
        elif format_name in HEIF_FORMATS:
            result["type_specific"] = extract_heif_specific(image)
        else:
            result["type_specific"] = {
                "note": f"No specialized parser for format {format_name or 'unknown'}"
            }
    except Exception as exc:
        result["warnings"].append(f"Format-specific parse failed: {exc!r}")

    try:
        image.close()
    except Exception:
        pass

    return result


# Helpers

def _file_size(path: str) -> Optional[int]:
    try:
        return os.path.getsize(path)
    except Exception:
        return None


def _safe_open(path: str) -> Image.Image:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    return Image.open(path)


def _bit_depth(image: Image.Image) -> Optional[int]:
    info = getattr(image, "info", {}) or {}
    if "bitdepth" in info:
        try:
            return int(info["bitdepth"])
        except Exception:
            pass
    return MODE_TO_BITS.get(image.mode)


def _basic_image_info(image: Image.Image) -> Dict[str, Any]:
    width, height = image.size
    format_name = image.format
    mode = image.mode
    frames = getattr(image, "n_frames", 1)
    is_animated = getattr(image, "is_animated", False)

    return {
        "format": format_name,
        "mode": mode,
        "width": width,
        "height": height,
        "bit_depth_per_channel": _bit_depth(image),
        "frames": int(frames),
        "is_animated": bool(is_animated),
    }


# Format-specific extractors

def extract_jpeg_specific(image: Image.Image) -> Dict[str, Any]:
    """
    JPEG/JFIF specifics commonly exposed by Pillow.
    """
    info = getattr(image, "info", {}) or {}
    output: Dict[str, Any] = {
        "progressive": bool(info.get("progressive")) if "progressive" in info else None,
        "jfif": info.get("jfif"),
        "jfif_unit": info.get("jfif_unit"),       # 0: no units, 1: dpi, 2: dpc
        "jfif_density": info.get("jfif_density"), # (xdensity, ydensity)
        "quality": info.get("quality"),
        "subsampling": info.get("subsampling"),
    }
    return {key: val for key, val in output.items() if val is not None}


def extract_png_specific(image: Image.Image) -> Dict[str, Any]:
    """
    PNG specifics: bit depth, color type (derived from mode), interlace, textual chunks.
    """
    info = getattr(image, "info", {}) or {}

    # Collect textual chunks into a dict, if present
    text_chunks: Dict[str, Any] = {}
    if isinstance(info.get("text"), dict):
        text_chunks = dict(info["text"])
    else:
        for key in PNG_TEXT_KEYS:
            if key in info:
                text_chunks[key] = info[key]

    output: Dict[str, Any] = {
        "bit_depth": info.get("bitdepth"),
        "color_type_from_mode": image.mode,   # e.g., L, LA, RGB, RGBA, P
        "interlace": info.get("interlace"),   # 0 or 1
        "gamma": info.get("gamma"),
        "transparency": bool(info.get("transparency")) if "transparency" in info else None,
        "text": text_chunks or None,
    }
    return {key: val for key, val in output.items() if val is not None}


def extract_gif_specific(image: Image.Image) -> Dict[str, Any]:
    """
    GIF specifics: animation frames, loop count, per-frame duration
    """
    info = getattr(image, "info", {}) or {}
    output: Dict[str, Any] = {
        "is_animated": getattr(image, "is_animated", False),
        "frames": getattr(image, "n_frames", 1),
        "loop": info.get("loop"),                # number of loops (0 = forever)
        "duration_ms": info.get("duration"),     # ms per frame
        "background": info.get("background"),
        "transparency_index": info.get("transparency"),
    }
    return {key: val for key, val in output.items() if val is not None}


def extract_webp_specific(image: Image.Image) -> Dict[str, Any]:
    """
    WebP specifics exposed by Pillow: animation, lossless flag (when available), alpha.
    """
    info = getattr(image, "info", {}) or {}
    output: Dict[str, Any] = {
        "is_animated": getattr(image, "is_animated", False),
        "frames": getattr(image, "n_frames", 1),
        "loop": info.get("loop"),
        "duration_ms": info.get("duration"),
        "lossless": info.get("lossless"),
        "alpha": info.get("alpha"),        # True if has alpha (not always present)
    }
    return {key: val for key, val in output.items() if val is not None}


def extract_tiff_specific(image: Image.Image) -> Dict[str, Any]:
    """
    TIFF specifics: compression, photometric, resolution unit, extra samples, etc.
    Available keys depend on the TIFF and Pillow build.
    """
    info = getattr(image, "info", {}) or {}
    output: Dict[str, Any] = {
        "compression": info.get("compression"),
        "photometric": info.get("photometric"),
        "resolution_unit": info.get("resolution_unit"),  # 1: none, 2: inch, 3: cm
        "tile": info.get("tile"),                        # tiling info if present
        "extra_samples": info.get("extra_samples"),
        "predictor": info.get("predictor"),
        "fillorder": info.get("fillorder"),
        "orientation": info.get("orientation"),
    }
    return {key: val for key, val in output.items() if val is not None}


def extract_bmp_specific(image: Image.Image) -> Dict[str, Any]:
    """
    BMP specifics
    """
    info = getattr(image, "info", {}) or {}
    output: Dict[str, Any] = {
        "compression": info.get("compression"),
        "dpi": info.get("dpi"),
    }
    return {key: val for key, val in output.items() if val is not None}


def extract_heif_specific(image: Image.Image) -> Dict[str, Any]:
    """
    HEIF/HEIC/AVIF specifics
    """
    info = getattr(image, "info", {}) or {}
    output: Dict[str, Any] = {
        "brand": info.get("brand"),
        "major_brand": info.get("major_brand"),
        "minor_version": info.get("minor_version"),
        "compatible_brands": info.get("compatible_brands"),
        "is_animated": getattr(image, "is_animated", False),
        "frames": getattr(image, "n_frames", 1),
        "duration_ms": info.get("duration"),
    }
    return {key: val for key, val in output.items() if val is not None}