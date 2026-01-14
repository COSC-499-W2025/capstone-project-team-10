import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import FreqDist, pos_tag, ne_chunk
from nltk.tree import Tree
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class TextSummary:
    """Analyzes and Summarizes text using NLTK."""
    
    def __init__(self, text: str) -> None:
        """
        Initialize the TextSummary with text and perform initial processing.
        Takes a text string as input
        """
        # Point NLTK to the data folder in utils for downloaded files
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        project_nltk_data = os.path.join(project_root, "utils", "nltk_data")
        nltk.data.path.append(project_nltk_data)

        self.text = text
        self.stop_words = set(stopwords.words("english"))

        # Tokenize text into sentences
        self.sentences = sent_tokenize(text)
    
        # Tokenize each sentence into words
        sentence_word_lists = [
            [w for w in word_tokenize(s) if w.isalpha()]
            for s in self.sentences
        ]
        
        # Gets all words from the sentence_word_list
        self.words = [w for words in sentence_word_lists for w in words]
        
        # Filters words to lowercase and excludes stop words (the, a, and, is, etc.)
        self.words_lower = [
            w.lower() for w in self.words 
            if w.lower() not in self.stop_words
        ]
        
        # Filters sentences to lowercase and excludes stop words
        self.sentence_tokens = [
            [w.lower() for w in words if w.lower() not in self.stop_words]
            for words in sentence_word_lists
        ]

        if self.words:
            self.pos_tags = pos_tag(self.words)
        else:
            self.pos_tags = []
        
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def getCommonWords(self, amount: int) -> list[tuple[str, int]]:
        """
        Get the most common words in the text.
        Takes an integer for the number of words to return.
        Returns a list of (word, frequency) tuples.
        """
        # Create a distribution with the count of occurrences of each word
        word_frequency = FreqDist(self.words_lower)
        return word_frequency.most_common(amount)

    def getNamedEntities(self, entity_types = None) -> set[tuple[str,str]] :
        """
        Extract named entities from the text.
        Takes an optional list of entity types to filter for (e.g., ['PERSON', 'ORGANIZATION']).
        If no list is provided, returns all entity types.
        Returns a set of (entity_name, entity_type) tuples.
        """
        # Check if text is empty
        if not self.pos_tags:
            return set()

        # Apply named entity chunking to the POS tagged words
        chunked = ne_chunk(self.pos_tags, binary = False)
        entities = set()

        # Extract entity name and type from each tree node
        for subtree in chunked:
            if isinstance(subtree, Tree):
                entity_type = subtree.label()
                entity_name = " ".join(word for word, tag in subtree.leaves())

                # Filter by entity type if specified
                if entity_types is None or entity_type in entity_types:
                    entities.add((entity_name, entity_type))

        return entities
    
    def getSentiment(self, threshold: float = 0.05) -> dict[str, float | str]:
        """
        Analyze overall sentiment using sentence-level analysis.
        Takes an optional threshold (default 0.05) for classifying sentiment.
        Values between 0 to +- the threshold are considered neutral (-0.03 or 0.02).
        Returns a dictionary with sentiment classification and compound score.
        """
        
        # Handle empty text edge case
        if not self.sentences:
            return {'sentiment': 'neutral', 'compound_score': 0.0}
        
        # Calculate average compound score across all sentences
        total_compound = 0.0
        for sentence in self.sentences:
            scores = self.sentiment_analyzer.polarity_scores(sentence)
            total_compound += scores['compound']
        
        avg_compound = total_compound / len(self.sentences)
        
        # Classify sentiment based on threshold
        if avg_compound >= threshold:
            sentiment = 'positive'
        elif avg_compound <= -threshold:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment, 
            'compound_score': round(avg_compound, 3)
        }

    def getSummary(self, num_sentences: int = 5) -> str:
        """
        Generate an extractive summary based on word frequencies.
        Takes an integer for the number of sentences to include (default 5).
        Returns a string containing the most important sentences in original order.
        """
        # Calculate word frequencies from filtered words
        word_freq = FreqDist(self.words_lower)

        # Score each sentence by averaging its word frequencies
        sentence_scores = {}
        for idx, words in enumerate(self.sentence_tokens):
            score = sum(word_freq[w] for w in words) / len(words) if words else 0
            sentence_scores[idx] = score

        # Get top scoring sentences and sort by original order
        top_indices = sorted(sentence_scores.keys(), key=lambda i: sentence_scores[i], reverse=True)[:num_sentences]
        top_indices.sort()
        
        return ' '.join(self.sentences[i] for i in top_indices)

    def getStatistics(self) -> dict[str, int | float]:
        """
        Calculate basic text statistics.
        Returns a dictionary containing word count, unique words, sentence count, and lexical diversity.
        """
        # Get unique words from filtered word list
        unique_words = set(self.words_lower)

        return {
            'word_count': len(self.words_lower),
            'unique_words': len(unique_words),
            'sentence_count': len(self.sentences),
            'lexical_diversity': round(
                len(unique_words) / len(self.words_lower), 3
            ) if self.words_lower else 0
        }
    
    def generate_complexity_feedback(self, lexical_diversity):
        # Assess document complexity based on vocabulary diversity.
        if lexical_diversity >= 0.6:
            return "High - Advanced vocabulary, excellent vocabulary, varied and diverse word choices."
        elif lexical_diversity >= 0.4:
            return "Medium - Standard vocabulary, good use of varied but standard word choices."
        else:
            return "Low - Simple vocabulary, try using more varied vocabulary to engage readers."


    def generate_length_vocab_feedback(self, stats):
        # Length and vocabulary feedback
        if stats["word_count"] < 100:
            return "Consider adding more detail to fully develop your ideas."
        elif stats["word_count"] > 1000:
            if stats["lexical_diversity"] >= 0.6:
                return "Extensive detail and depth used to explore your ideas."
            if stats["lexical_diversity"] >= 0.4:
                return (
                    "Extensive depth and sufficient detail to explore your topic and ideas."
                )
            if stats["lexical_diversity"] < 0.4:
                return "Extensive length but consider adding more depth to your writing on the topics at hand."
        elif stats["word_count"] >= 100 & stats["word_count"] < 1000:
            if stats["lexical_diversity"] >= 0.6:
                return "Average length and excellent depth and detail used to explore your ideas."
            if stats["lexical_diversity"] >= 0.4:
                return (
                    "Average length and sufficient detail to explore your topic and ideas."
                )
            if stats["lexical_diversity"] < 0.4:
                return "Average length but consider adding more depth to your writing on the topics at hand."
        else:
            return None


    def generate_sentence_feedback(self, stats):
        # Sentence structure
        avg_sentence_length = (
            stats["word_count"] / stats["sentence_count"]
            if stats["sentence_count"] > 0
            else 0
        )
        if avg_sentence_length > 30:
            return "Consider breaking up complex sentences for better readability."
        elif avg_sentence_length < 10:
            return "Consider combining related ideas for better flow."
        else:
            return "Well formed and approprite sentences that demonstrates understanding of writing conventions."


    def generate_sentiment_feedback(self, sentiment):
        # Sentiment feedback
        # Default Threshold is +- 0.05
        if sentiment["compound_score"] < -0.05:
            return "Overall negative sentiment within your writing. Consider reframing content more positively if and where appropriate or more neutrally if aiming for a professional level output"
        elif sentiment["compound_score"] > 0.05:
            return "Overall positive sentiment within your writing. Consider reframing content more neutrally if aiming for a professional writing piece."
        else:
            return "Overall neutral sentiment within your writing. Professional standard sentiment of writing, if you are aiming for a more positive or negative sentiment consider changing your word choices."

    
    def generate_text_analysis_data(self, num_keywords: int = 10, num_sentences: int = 3) -> dict:
        """
        Final generation function to return all text data in a single dict.
        Args:
            num_keywords: the number of unique keywords
            num_sentences: the number of sentences in the text summary
        Returns:
            A dictionary containing all analysis data:
            - filtered_word_count: Count of words excluding stop words
            - unique_words: Count of unique words
            - sentence_count: Number of sentences
            - lexical_diversity: Ratio of unique words to total words
            - top_keywords: List of (word, frequency) tuples
            - sentiment: Sentiment classification (positive/negative/neutral)
            - sentiment_score: Compound sentiment score
            - named_entities: List of (entity_name, entity_type) tuples
            - summary: Extractive summary string
            - complexity: Feedback about vocabulary complexity
            - depth: Feedback about length and vocabulary
            - structure: Feedback about sentence structure
            - sentiment_insight: Feedback about sentiment
        """
        stats = self.getStatistics()
        sentiment = self.getSentiment()
        analysis = {
            "filtered_word_count": stats['word_count'],
            "unique_words": stats['unique_words'],
            "sentence_count": stats['sentence_count'],
            "lexical_diversity": stats['lexical_diversity'],
            "top_keywords": self.getCommonWords(num_keywords),
            "sentiment": sentiment['sentiment'],
            "sentiment_score": sentiment['compound_score'],
            "named_entities": list(self.getNamedEntities()),
            "summary": self.getSummary(num_sentences=num_sentences),      
        }

        analysis["complexity"] = self.generate_complexity_feedback(stats['lexical_diversity'])
        analysis["depth"] = self.generate_length_vocab_feedback(stats)
        analysis["structure"] = self.generate_sentence_feedback(stats)
        analysis["sentiment_insight"] = self.generate_sentiment_feedback(sentiment)

        return analysis
