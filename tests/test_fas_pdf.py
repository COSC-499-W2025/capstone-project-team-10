import pytest
import os
import src.fas.fas_pdf as pdfr

TESTPATH1 = os.path.join("tests", "testdata", "test_fas_pdf","samplePDF1.pdf")
TESTPATH2 = os.path.join("tests", "testdata", "test_fas_pdf","samplePDF2.pdf")
TESTPATH3 = os.path.join("tests", "testdata", "test_fas_pdf","sampleText1.txt")
TESTPATH4 = os.path.join("tests", "testdata", "test_fas_pdf","samplePDF4.pdf")

class TestPDF:

    @pytest.fixture
    def sample_pdf(self):
        return pdfr.extract_pdf_data(TESTPATH1)
    
    @pytest.fixture
    def sample_pdf2(self):
        return pdfr.extract_pdf_data(TESTPATH2)
    
    @pytest.fixture
    def sample_pdf4(self):
        return pdfr.extract_pdf_data(TESTPATH4)
    
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            pdfr.extract_pdf_data(r"C:\badpath.pdf")
    
    def test_invalid_file_type(self):
        with pytest.raises(Exception):
            pdfr.extract_pdf_data(TESTPATH3)

    def test_filepath(self, sample_pdf):
        assert sample_pdf["file_path"] == TESTPATH1
        assert isinstance(sample_pdf["file_path"], str)

    def test_file_size(self, sample_pdf):
        assert sample_pdf["file_size_bytes"] > 0
        assert isinstance(sample_pdf["file_size_bytes"], int)

    def test_metadata(self, sample_pdf):
        metadata = sample_pdf["pdf_metadata"]
        assert metadata is None or isinstance(metadata, dict)
    
        # Check metadata fields - using .get() with default "Unknown"
        author = metadata.get("Author", "Unknown") if metadata else "Unknown"
        assert isinstance(author, str)
        assert author is not None
        
        creator = metadata.get("Creator", "Unknown") if metadata else "Unknown"
        assert isinstance(creator, str)
        assert creator is not None
        
        producer = metadata.get("Producer", "Unknown") if metadata else "Unknown"
        assert isinstance(producer, str)
        assert producer is not None
        
        title = metadata.get("Title", "Unknown") if metadata else "Unknown"
        assert isinstance(title, str)
        assert title is not None
        
        subject = metadata.get("Subject", "Unknown") if metadata else "Unknown"
        assert isinstance(subject, str)
        assert subject is not None
        
        keywords = metadata.get("Keywords", "Unknown") if metadata else "Unknown"
        assert isinstance(keywords, str)
        assert keywords is not None

    def test_count_properties_match_lists(self, sample_pdf):
        assert sample_pdf["counts"]["images"] == len(sample_pdf["images"])
        assert sample_pdf["counts"]["tables"] == len(sample_pdf["tables"])
        assert sample_pdf["counts"]["hyperlinks"] == len(sample_pdf["hyperlinks"])

    def test_multi_page_extraction(self, sample_pdf2):
        assert sample_pdf2["counts"]["pages"] > 1
        assert isinstance(sample_pdf2["counts"]["pages"], int)
        assert len(sample_pdf2["text"]) > 0
        assert sample_pdf2["counts"]["words"] > 0
        assert sample_pdf2["counts"]["characters"] > 0

    def test_pdf_no_tables_links_images(self, sample_pdf2):
        assert sample_pdf2["counts"]["images"] == 0
        assert len(sample_pdf2["images"]) == 0

        assert sample_pdf2["counts"]["hyperlinks"] == 0
        assert len(sample_pdf2["hyperlinks"]) == 0

        assert sample_pdf2["counts"]["tables"] == 0
        assert len(sample_pdf2["tables"]) == 0

    def test_page_count(self, sample_pdf, sample_pdf2):
        assert sample_pdf["counts"]["pages"] == 1
        assert sample_pdf2["counts"]["pages"] == 6
        assert isinstance(sample_pdf["counts"]["pages"], int)

    def test_image_count(self, sample_pdf):
        assert sample_pdf["counts"]["images"] > 0 

    def test_table_count(self, sample_pdf):
        assert sample_pdf["counts"]["tables"] > 0 

    def test_link_count(self, sample_pdf):
        assert sample_pdf["counts"]["hyperlinks"] > 0

    def test_word_count(self, sample_pdf):
        assert sample_pdf["counts"]["words"] > 0

    def test_ligatures(self, sample_pdf4):
        assert "fi" in sample_pdf4["text"] # Check if fi is correctly found
        assert "firearm" in sample_pdf4["text"] # Check if fi is correctly displayed in word
        assert "question" in sample_pdf4["text"] # Check if ti is correctly displayed in word

    def test_text_analysis(self,sample_pdf4):
        assert len(sample_pdf4["top_keywords"]) > 0
        assert sample_pdf4["unique_words"] != 0
        assert sample_pdf4["sentence_count"] != 0
        assert sample_pdf4["lexical_diversity"] != 0
        assert sample_pdf4["filtered_word_count"] != 0
        assert sample_pdf4["sentiment"] != None
        assert len(sample_pdf4["summary"]) > 5
        assert sample_pdf4["complexity"] != None
        assert sample_pdf4["depth"] != None
        assert sample_pdf4["structure"] != None
        assert sample_pdf4["sentiment_insight"] != None