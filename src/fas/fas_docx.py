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

            # Add simple insight about word choice in document
            metadata["complexity"] = generate_complexity_feedback(stats['lexical_diversity'])

            # Add isnight based on length and vocab used
            metadata["depth"] = generate_length_vocab_feedback(stats)

            #Add insight based on sentence structure
            metadata["structure"] = generate_sentence_feedback(stats)

            # Add insight based on sentiment
            metadata["sentiment_insight"] = generate_sentiment_feedback(sentiment)

        return metadata
    except Exception as e:
        return {"error": str(e)}
    
def generate_complexity_feedback(lexical_diversity):
    # Assess document complexity based on vocabulary diversity.
    if lexical_diversity >= 0.6:
        return "High - Advanced vocabulary, excellent vocabulary, varied and diverse word choices."
    elif lexical_diversity >= 0.4:
        return "Medium - Standard vocabulary, good use of varied but standard word choices."
    else:
        return "Low - Simple vocabulary, try using more varied vocabulary to engage readers."

def generate_length_vocab_feedback(stats):
    # Length and vocabulary feedback
    if stats['word_count'] < 100:
        return "Consider adding more detail to fully develop your ideas."
    elif stats['word_count'] > 1000:
        if stats['lexical_diversity'] >= 0.6:
            return "Extensive detail and depth used to explore your ideas."
        if stats['lexical_diversity'] >= 0.4:
            return "Extensive depth and sufficient detail to explore your topic and ideas."
        if stats['lexical_diversity'] < 0.4:
            return "Extensive length but consider adding more depth to your writing on the topics at hand." 
    elif stats['word_count'] >= 100 & stats['word_count'] < 1000:
        if stats['lexical_diversity'] >= 0.6:
            return "Average length and excellent depth and detail used to explore your ideas."
        if stats['lexical_diversity'] >= 0.4:
            return "Average length and sufficient detail to explore your topic and ideas."
        if stats['lexical_diversity'] < 0.4:
            return "Average length but consider adding more depth to your writing on the topics at hand." 
    else:
        return None

def generate_sentence_feedback(stats): 
    # Sentence structure
    avg_sentence_length = stats['word_count'] / stats['sentence_count'] if stats['sentence_count'] > 0 else 0
    if avg_sentence_length > 30:
        return "Consider breaking up complex sentences for better readability."
    elif avg_sentence_length < 10:
        return "Consider combining related ideas for better flow."
    else:
        return "Well formed and approprite sentences that demonstrates understanding of writing conventions."

def generate_sentiment_feedback(sentiment):    
    # Sentiment feedback
    # Default Threshold is +- 0.05
    if sentiment['compound_score'] < -0.05:
        return "Overall negative sentiment within your writing. Consider reframing content more positively if and where appropriate or more neutrally if aiming for a professional level output"
    elif sentiment['compound_score'] > 0.05:
        return "Overall positive sentiment within your writing. Consider reframing content more neutrally if aiming for a professional writing piece."
    else:
        return "Overall neutral sentiment within your writing. Professional standard sentiment of writing, if you are aiming for a more positive or negative sentiment consider changing your word choices."