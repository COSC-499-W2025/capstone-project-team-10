from docx import Document

def extract_docx_data(path):
    doc = Document(path)

    # This can be used when finding keywords for summary, analysis, and or ranking depending on implememntation
    text = "\n".join(p.text for p in doc.paragraphs)

    # Metadata extraction
    core = doc.core_properties
    metadata = {
        "author": core.author,
        "title": core.title,
        "subject": core.subject,
        "created": core.created,
        "modified": core.modified,
        "keywords": core.keywords,
        "category": core.category,
        "comments": core.comments,
        # This is to get stats of the content of the document
        "num_paragraphs": len(doc.paragraphs),
        "num_tables": len(doc.tables),
        "num_chars": len(text),
        "num_words": len(text.split()),
    }
    print(metadata)
    return metadata