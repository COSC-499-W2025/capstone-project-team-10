# src/fas/fas_extra_data.py

import os
from typing import Any, Optional

from utils.extension_mappings import CODING_FILE_EXTENSIONS as em
from utils.libraries_mappings import LIBRARY_SKILL_MAP as lsm
from src.fas.fas_code_reader import CodeReader


def get_file_extra_data(file_path: str, file_type: str) -> Optional[Any]:
    try:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        print(f"Scanning: {file_path}")

        metadata = None

        match file_type:
            case "pdf":
                from src.fas import fas_pdf
                metadata = fas_pdf.extract_pdf_data(file_path)

            case "docx":
                from src.fas import fas_docx
                metadata = fas_docx.extract_docx_data(file_path)

            case "odt":
                from src.fas import fas_odt
                metadata = fas_odt.extract_odt_data(file_path)

            case "rtf":
                from src.fas import fas_rtf
                metadata = fas_rtf.extract_rtf_data(file_path)

            case "xlsx" | "xls":
                from src.fas import fas_excel
                return fas_excel.extract_excel_data(file_path)

            case "psd" | "photoshop":
                from src.fas import fas_photoshop
                return fas_photoshop.extract_photoshop_data(file_path)

            case (
                "jpeg" | "jpg" | "png" | "gif" | "webp" |
                "tiff" | "bmp" | "heif" | "heic" | "avif"
            ):
                from src.fas import fas_image_format
                return fas_image_format.analyze_image(file_path)

            case "md" | "markdown":
                from src.fas.fas_md import Markdown
                md = Markdown(file_path)
                return {
                    "headers": md.get_headers(),
                    "header_hierarchy": md.get_header_hierarchy(),
                    "word_count": md.get_word_counts(),
                    "code_blocks": md.get_code_blocks(),
                    "paragraphs": md.get_paragraphs(),
                }

            case _ if ext in em:
                return _analyze_code_file(file_path)

            case "git":
                from src.fas.fas_git_grouping import GitGrouping
                return GitGrouping().add_repository(file_path)

            case _:
                return None

        # ---------- Post-processing for text-like documents ----------
        if file_type in ("docx", "odt", "rtf", "pdf") and isinstance(metadata, dict):
            _clean_summary(metadata)
            metadata["key_skills"] = _extract_text_skills(metadata)

        return metadata

    except ModuleNotFoundError:
        print(f"No handler found for file type: {file_type}")
        return None


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _analyze_code_file(file_path: str) -> dict:
    reader = CodeReader(file_path)

    metadata = {
        "language": reader.filetype,
        "libraries": reader.libraries,
        "complexity": reader.complexity,
        "oop": reader.oop,
    }

    skills = []

    if reader.filetype:
        skills.append(f"{reader.filetype.capitalize()} programming")

    if isinstance(reader.libraries, list):
        for lib in reader.libraries:
            if lib in lsm:
                skills.append(lsm[lib])

    if isinstance(reader.oop, dict):
        if reader.oop.get("classes"):
            skills.append("Object-oriented programming (OOP)")
        if reader.oop.get("functions"):
            skills.append("Modular function design")

    if isinstance(reader.complexity, dict):
        est = reader.complexity.get("estimated")
        if est and est != "O(1)":
            skills.append("Algorithmic complexity analysis")

    metadata["key_skills"] = list(set(skills))
    return metadata


def _clean_summary(metadata: dict) -> None:
    summary = metadata.get("summary")
    if isinstance(summary, str):
        summary = summary.replace("\n", " ").replace("\r", " ")
        metadata["summary"] = " ".join(summary.split())


def _extract_text_skills(metadata: dict) -> list[str]:
    skills = []
    for key in ("complexity", "depth", "structure", "sentiment_insight"):
        if key in metadata:
            skill = feedback_to_skill(metadata[key])
            if skill:
                skills.append(skill)
    return skills


# -------------------------------------------------------------------
# Feedback → Skill mapping (moved here)
# -------------------------------------------------------------------

def feedback_to_skill(feedback: str) -> Optional[str]:
    if not feedback:
        return None

    f = feedback.lower()

    if "high - advanced vocabulary" in f:
        return "Advanced Vocabulary"
    if "medium - standard vocabulary" in f:
        return "Strong Vocabulary"
    if "low - simple vocabulary" in f:
        return "Basic Vocabulary"

    if "extensive detail and depth used to explore your ideas" in f:
        return "In-Depth Writing"
    if "extensive depth and sufficient detail" in f:
        return "Thorough Writing"
    if "extensive length but consider adding more depth" in f:
        return "High Output Writing"
    if "average length and excellent depth and detail" in f:
        return "Balanced Writing"
    if "average length and sufficient detail" in f:
        return "Clear Writing"
    if "average length but consider adding more depth" in f:
        return "Developing Writing"
    if "consider adding more detail to fully develop your ideas" in f:
        return "Concise Writing"

    if "breaking up complex sentences" in f:
        return "Complex Sentence Structure"
    if "combining related ideas for better flow" in f:
        return "Sentence Flow"
    if "well formed and approprite sentences" in f:
        return "Strong Writing Structure"

    if "overall negative sentiment" in f:
        return "Emotive Writing"
    if "overall positive sentiment" in f:
        return "Positive Tone"
    if "overall neutral sentiment" in f:
        return "Professional Tone"

    return None
