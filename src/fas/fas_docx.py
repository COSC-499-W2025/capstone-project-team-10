from docx import Document
from fas.fas_text_analysis import TextSummary

def extract_docx_data(path):
    try:
        doc = Document(path)

        # This can be used when finding keywords for summary, analysis, and or ranking depending on implememntation
        text = "\n".join(p.text for p in doc.paragraphs)

        analyzer = TextSummary(text) if text.strip() else None

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
        
        # If text exists, add text analysis
        if analyzer:
            # Get statistics
            stats = analyzer.getStatistics()
            metadata.update({
                "filtered_word_count": stats['word_count'],
                "unique_words": stats['unique_words'],
                "sentence_count": stats['sentence_count'],
                "lexical_diversity": stats['lexical_diversity']
            })

            # Add top 10 keywords
            metadata["top_keywords"] = analyzer.getCommonWords(10)

            # Add sentiment analysis
            sentiment = analyzer.getSentiment()
            metadata["sentiment"] = sentiment['sentiment']
            metadata["sentiment_score"] = sentiment['compound_score']

            # Add named entities
            entities = analyzer.getNamedEntities()
            metadata["named_entities"] = list(entities)

            # Add 3 sentence summary
            metadata["summary"] = analyzer.getSummary(num_sentences=3)

        return metadata
    except Exception as e:
        return {"error": str(e)}