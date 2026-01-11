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