import os
import nltk

def setup_nltk_data():
    """
    Ensures all required NLTK data packages are installed locally under utils/nltk_data.
    Safe for Windows, macOS, and Linux.
    Compatible with NLTK 3.9+
    """

    # Determine absolute path to local nltk_data folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nltk_data_path = os.path.join(base_dir, "nltk_data")

    # Create folder if missing
    os.makedirs(nltk_data_path, exist_ok=True)

    # Add to nltk data search path (prepend to prioritize local)
    if nltk_data_path not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_path)

    required_packages = [
        "punkt_tab",                        # Sentence + word tokenization
        "stopwords",                        # Stop word filtering
        "averaged_perceptron_tagger_eng",   # English POS tagging
        "maxent_ne_chunker_tab",            # Named entity recognition
        "words",                            # NE recognition dependency
        "vader_lexicon"                     # Sentiment analysis
    ]

    for pkg in required_packages:
        try:
            nltk.download(pkg, download_dir=nltk_data_path, quiet=False)
        except Exception as e:
            print(f"Warning: Could not download {pkg}: {e}")

if __name__ == "__main__":
    setup_nltk_data()