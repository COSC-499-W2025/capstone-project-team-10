import nltk
import string


class TextSummary:
    def __init__(self, textblock):
        self.text = textblock
        self.sentences = []
        self.words = []

        self.commonWord = None

    def tokenizeText(self):
        # Creates a set of common english words like ("a", "is", "the")
        stop_words = set(nltk.corpus.stopwords.words('english'))

        # Splits the text block into sentences
        self.sentences = nltk.sent_tokenize(self.text)

        # Splits the sentences into words removing punctuation and stop_words
        self.words = []
        for sentence in self.sentences:
            # Tokenize sentence into individual words
            tokens = nltk.word_tokenize(sentence)
            
            # Filter and clean each word
            for word in tokens:
                # Only keep alphabetic words (no punctuation or numbers)
                if word.isalpha():
                    word_lower = word.lower()
                    # Skip common words like "the", "and", etc.
                    if word_lower not in stop_words:
                        self.words.append(word_lower)

    def getCommonWord(self):
        # Returns the most common word and the number of times it appears
        word_frequency = nltk.FreqDist(self.words)
        most_common = word_frequency.most_common(1)
        print(most_common)

    def getCommonWords(self, number):
        # Finds the top most common 
        word_frequency = nltk.FreqDist(self.words)
        most_common = word_frequency.most_common(number)
        print(most_common)

    
def main():

    beeMovieScriptFile = r"tests\testdata\test_fss\testScanFile"
    with open(beeMovieScriptFile, 'r') as file:
        try:
            beeMovieScript = file.read()
            text_summary = TextSummary(beeMovieScript)
            text_summary.tokenizeText()
            text_summary.getCommonWords(15)
        except Exception as e:
            print(f"Error {e}")

if __name__ == "__main__":
    main()