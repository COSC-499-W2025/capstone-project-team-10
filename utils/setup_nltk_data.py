import os
import nltk

def setup_nltk_data():
    """
    Ensures all required NLTK data packages are installed locally under utils/nltk_data.
    Safe for Windows, macOS, and Linux.
    """

    # Determine absolute path to local nltk_data folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nltk_data_path = os.path.join(base_dir, "nltk_data")

    # Create folder if missing
    os.makedirs(nltk_data_path, exist_ok=True)

    # Add to nltk data search path
    if nltk_data_path not in nltk.data.path:
        nltk.data.path.append(nltk_data_path)

    required_packages = [
        "punkt",                       # Sentence + word tokenization
        "stopwords",                   # Stop word filtering
        "averaged_perceptron_tagger",  # POS tagging
        "maxent_ne_chunker",           # Named entity recognition
        "words",                       # NE recognition dependency
        "vader_lexicon"                # Sentiment analysis
    ]

    for pkg in required_packages:
        nltk.download(pkg, download_dir=nltk_data_path, quiet=False)

if __name__ == "__main__":
    setup_nltk_data()