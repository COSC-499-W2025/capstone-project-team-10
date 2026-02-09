import os

def infer_unknown_file(file_path: str) -> dict:
    """
    Fallback analysis for unknown or uncommon file types.
    Ensures human-readable metadata and key_skills.
    """

    size = os.path.getsize(file_path)

    # ---- Detect text vs binary ----
    try:
        with open(file_path, "rb") as f:
            sample = f.read(512)
        is_text = b"\x00" not in sample
    except:
        is_text = False

    if is_text:
        try:
            with open(file_path, "r", errors="ignore") as f:
                lines = f.readlines()

            has_comments = any(
                l.strip().startswith(("#", "//", ";")) for l in lines
            )
            has_blocks = any("{" in l or "}" in l for l in lines)

            skills = [
                "Text file analysis",
                "File structure interpretation",
            ]

            if has_comments:
                skills.append("Code or configuration comprehension")

            if has_blocks:
                skills.append("Structured syntax understanding")

            return {
                "file_category": "Unknown text-based file",
                "description": "Unrecognized text file analyzed using structural heuristics",
                "line_count": len(lines),
                "key_skills": list(set(skills)),
            }

        except:
            pass

    # ---- Binary fallback ----
    skills = [
        "Binary file handling",
        "Low-level file inspection",
    ]

    if size > 5 * 1024 * 1024:
        skills.append("Large file handling")

    return {
        "file_category": "Unknown binary file",
        "description": "Unrecognized binary file inferred from content analysis",
        "size_bytes": size,
        "key_skills": skills,
    }
