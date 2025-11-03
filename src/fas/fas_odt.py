from odf.opendocument import load
from odf.text import P
from odfdo import Document

def extract_odt_data(path):
    try:
        doc = load(path)
        paras = doc.getElementsByType(P)
        text = "\n".join(p.firstChild.data if p.firstChild else "" for p in paras)

        doc = Document(path)

        meta = doc.meta

        metadata = {
            "title": meta.title,
            "author": meta.initial_creator,
            "subject": meta.subject,
            "created": meta.creation_date,
            "modified": meta.get_modification_date,
            "num_paragraphs": len(paras),
            "num_chars": len(text),
            "num_words": len(text.split()),
        }

        return metadata
    except Exception as e:
        return {"error": str(e)}
