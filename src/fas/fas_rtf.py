import datetime
import re
from striprtf.striprtf import rtf_to_text
from src.fas.fas_text_analysis import TextSummary

def extract_rtf_data(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            rtf = f.read()

        text = rtf_to_text(rtf)

        analyzer = TextSummary(text) if text.strip() else None

        title = extract_specific_data(rtf, "title")
        author = extract_specific_data(rtf, "author")
        subject = extract_specific_data(rtf, "subject")

        c_date = extract_datetime(rtf, "creatim")
        r_date = extract_datetime(rtf, "revtim")

        # RTF files do not have standardized metadata and sometimes they dont have any at all, extraction of title, author, and subject is only possible if the RTF was made in Word.
        metadata = {
            "author": author,
            "title": title,
            "subject": subject,
            "created": c_date,
            "modified": r_date,
            "num_chars": len(text),
            "num_words": len(text.split()),
            "num_paragraphs": len(text.split('\n\n')),
        }

        # If text exists, add text analysis
        if analyzer:
            metadata.update(analyzer.generate_text_analysis_data(10, 3))

        return metadata
    except Exception as e:
        return {"error": str(e)}

def extract_datetime(rtf, str):
    # As the creatim and revtim are stored in the RTF they must be extracted, this combines the plain text to form a datetime object for consistency with other file types.
    block = re.search(r'{\\'+str+'([^}]*)}', rtf)
    if not block:
        return None

    fields = dict(re.findall(r'\\([a-zA-Z]+)(\d+)', block.group(1)))
    yr = int(fields.get("yr"))
    mo = int(fields.get("mo"))
    dy = int(fields.get("dy"))
    hr = int(fields.get("hr", 0))
    minute = int(fields.get("min", 0))

    return datetime.datetime(yr, mo, dy, hr, minute)

def extract_specific_data(rtf, str):
    # As RTF only has specific metadata if created via Word, this will fill the value with "None" if it isnt present to stop errors
    block = re.search(r'{\\'+str+'+([^}]*)}', rtf)
    if not block:
        return None
    
    value = block.group(1).strip("} {")

    return value