from odf.opendocument import load
from odf.text import P
from odfdo import Document
from fas.fas_text_analysis import TextSummary

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
