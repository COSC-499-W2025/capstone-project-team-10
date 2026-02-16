import os
from src.fas.fas_text_analysis import TextSummary


def infer_unknown_file(file_path: str) -> dict:
    """
    Fallback analysis for unknown or uncommon file types.
    Uses FAS text analysis for text-based files.
    """

    size = os.path.getsize(file_path)

    # ---- Detect text vs binary ----
    try:
        with open(file_path, "rb") as f:
            sample = f.read(512)
        is_text = b"\x00" not in sample
    except Exception:
        is_text = False

    # ---- Text fallback ----
    if is_text:
        try:
            with open(file_path, "r", errors="ignore") as f:
                text = f.read()

            metadata = {
                "file_category": "Unknown text-based file",
                "description": "Unrecognized text file analyzed using FAS text analysis",
                "size_bytes": size,
            }

            if text.strip():
                analyzer = TextSummary(text)
                metadata.update(
                    analyzer.generate_text_analysis_data(
                        num_keywords=10,
                        num_sentences=3
                    )
                )

            return metadata

        except Exception as e:
            return {
                "file_category": "Unknown text-based file",
                "description": "Text detected but analysis failed",
                "size_bytes": size,
                "error": str(e),
            }

    # ---- Binary fallback ----
    return {
        "file_category": "Unknown binary file",
        "description": "Unrecognized binary file inferred from content analysis",
        "size_bytes": size,
    }
