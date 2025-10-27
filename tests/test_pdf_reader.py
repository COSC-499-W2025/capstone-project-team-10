import pytest
import src.fas.fas_pdf as pdfr
from unittest.mock import patch

class TestPDF:

    @pytest.fixture
    def sample_pdf(self):
        return pdfr.PDFReader(r"tests\sample_files\samplePDF1.pdf")
    
    @pytest.fixture
    def sample_pdf2(self):
        return pdfr.PDFReader(r"tests\sample_files\samplePDF2.pdf")
    
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            pdfr.PDFReader(r"C:\badpath.pdf")
    
    def test_invalid_file_type(self):
        with pytest.raises(Exception):
            pdfr.PDFReader(r"tests\sample_files\sampleText1.txt")

    def test_filepath(self, sample_pdf):
        assert sample_pdf.filepath == r"tests\sample_files\samplePDF1.pdf"
        assert isinstance(sample_pdf.filepath, str)

    def test_file_size(self, sample_pdf):
        assert sample_pdf.file_size > 0
        assert isinstance(sample_pdf.file_size, int)

    def test_metadata(self,sample_pdf):
        assert sample_pdf.data is None or isinstance(sample_pdf.data, dict)
    
        assert isinstance(sample_pdf.author, str)
        assert sample_pdf.author is not None
        
        assert isinstance(sample_pdf.creator, str)
        assert sample_pdf.creator is not None
        
        assert isinstance(sample_pdf.producer, str)
        assert sample_pdf.producer is not None
        
        assert isinstance(sample_pdf.title, str)
        assert sample_pdf.title is not None
        
        assert isinstance(sample_pdf.subject, str)
        assert sample_pdf.subject is not None
        
        assert isinstance(sample_pdf.keywords, str)
        assert sample_pdf.keywords is not None

    def test_count_properties_match_lists(self, sample_pdf):
        assert sample_pdf.image_count == len(sample_pdf.images)
        assert sample_pdf.table_count == len(sample_pdf.tables)
        assert sample_pdf.link_count == len(sample_pdf.links)

    def test_multi_page_extraction(self, sample_pdf2):
        assert sample_pdf2.page_count > 1
        assert isinstance(sample_pdf2.page_count, int)
        assert len(sample_pdf2.text) > 0
        assert sample_pdf2.word_count > 0
        assert sample_pdf2.char_count > 0

    def test_pdf_no_tables_links_images(self, sample_pdf2):
        assert sample_pdf2.image_count == 0
        assert len(sample_pdf2.images) == 0

        assert sample_pdf2.link_count == 0
        assert len(sample_pdf2.links) == 0

        assert sample_pdf2.table_count == 0
        assert len(sample_pdf2.tables) == 0

    def test_page_count(self, sample_pdf, sample_pdf2):
        assert sample_pdf.page_count == 1
        assert sample_pdf2.page_count == 6
        assert isinstance(sample_pdf.page_count, int)

    def test_image_count(self, sample_pdf):
        assert sample_pdf.image_count > 0 

    def test_table_count(self, sample_pdf):
        assert sample_pdf.table_count > 0 

    def test_link_count(self, sample_pdf):
        assert sample_pdf.link_count > 0

    def test_word_count(self, sample_pdf):
        assert sample_pdf.word_count > 0