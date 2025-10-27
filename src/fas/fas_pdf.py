import os
import re
import pdfplumber as plum
import fitz

class PDFReader:
    """
    Extracts data from PDF files including basic data, text, tables, images, and links.
    Uses pdfplumber for text and table extraction and PyMuPDF (fitz) for image and link extraction.
    """
    
    def __init__(self, filepath: str):
        """
        Initializes PDFReader and calls the extract_pdf_data() method
        Args:
            filepath: Path to the PDF file to extract data from
        """
        self.filepath = filepath

        # Basic Data
        self.file_size = 0
        self.data = None
        self.author = 'Unknown'
        self.creator = 'Unknown'
        self.producer = 'Unknown'
        self.title = 'Unknown'
        self.subject = 'Unknown'
        self.keywords = 'Unknown'
        self.page_count = 0

        # Text Data
        self.text = ''
        self.word_count = 0
        self.line_count = 0
        self.char_count = 0

        # Collections
        self.images = []
        self.tables = []
        self.links = []
        
        # Extract all data on initialization
        self.extract_pdf_data()
    
    @property
    def image_count(self) -> int:
        return len(self.images)
    
    @property
    def table_count(self) -> int:
        return len(self.tables)
    
    @property
    def link_count(self) -> int:
        return len(self.links)
    
    def extract_pdf_data(self):
        """
        Main extraction method that opens the pdf with both pdfplumber and pymupdf libraries.
        Calls the extraction helper methods.
        """
        try:
            self.file_size = os.path.getsize(self.filepath)
            
            # Open documents with pdfplumber and pymupdf (fitz) and calls extraction methods
            with plum.open(self.filepath) as pdf, fitz.open(self.filepath) as doc:
                self.extract_basic_data(pdf)
                self.extract_text_and_tables(pdf)
                self.extract_images_and_links(doc)
                
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {self.filepath}")
        except Exception as e:
            raise Exception(f"Error analyzing PDF: {str(e)}")

    def extract_basic_data(self, pdf):
        """
        Extracts basic data from PDF using pdfplumber library.
        Args:
            pdf: pdfplumber PDF object
        """
        self.data = pdf.metadata
        self.page_count = len(pdf.pages)
        
        if self.data:
            self.author = self.data.get('Author', 'Unknown')
            self.creator = self.data.get('Creator', 'Unknown')
            self.producer = self.data.get('Producer', 'Unknown')
            self.title = self.data.get('Title', 'Unknown')
            self.subject = self.data.get('Subject', 'Unknown')
            self.keywords = self.data.get('Keywords', 'Unknown')

    def extract_text_and_tables(self, pdf):
        """
        Extracts text and table data from PDF using pdfplumber.
        Calculates word count, character count, and line count.
        Args:
            pdf: pdfplumber PDF object
        """
        text_parts = []
        word_count = 0
        
        for page_num, page in enumerate(pdf.pages, 1):
            # Extract text
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
                # Split on whitespace and filter out single-character symbols
                words = page_text.split()
                filtered_words = [w for w in words if not (len(w) == 1 and not w.isalnum())]
                word_count += len(filtered_words)
            
            # Extract tables
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables, 1):
                self.tables.append({
                    'page': page_num,
                    'table_number': table_idx,
                    'data': table,
                    'rows': len(table),
                    'columns': len(table[0]) if table and table[0] else 0
                })
        
        # Set text-related attributes
        self.text = "\n".join(text_parts)
        self.word_count = word_count
        self.char_count = len(self.text)
        self.line_count = self.text.count('\n')

    def extract_images_and_links(self, doc):
        """
        Extracts image and hyperlink data from PDF using PyMuPDF (fitz).
        Args:
            doc: PyMuPDF document object
        """
        for page_num, page in enumerate(doc, 1):
            # Extract images
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                
                self.images.append({
                    'page': page_num,
                    'image_number': img_index + 1,
                    'image_bytes': base_image["image"],
                    'extension': base_image["ext"],
                    'width': base_image["width"],
                    'height': base_image["height"]
                })
            
            # Extract links
            links = page.get_links()
            for link in links:
                if 'uri' in link:
                    self.links.append({
                        'page': page_num,
                        'url': link['uri']
                    })