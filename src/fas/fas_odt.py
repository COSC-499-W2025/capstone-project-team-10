from odf.opendocument import load
from odf.text import P
from odfdo import Document
from src.fas.fas_text_analysis import TextSummary

def extract_odt_data(path):
    try:
        doc = load(path)
        paras = doc.getElementsByType(P)
        text = "\n".join(p.firstChild.data if p.firstChild else "" for p in paras)

        analyzer = TextSummary(text) if text.strip() else None

        doc = Document(path)

        meta = doc.meta

        metadata = {
            "title": meta.title,
            "author": meta.initial_creator,
            "subject": meta.subject,
            "created": meta.creation_date,
            "modified": meta.date,
            "num_paragraphs": len(paras),
            "num_chars": len(text),
            "num_words": len(text.split()),
        }

        # If text exists, add text analysis
        if analyzer:
            metadata.update(analyzer.generate_text_analysis_data(10, 3))

        return metadata
    except Exception as e:
        return {"error": str(e)}
    