import os
import pdfplumber as plum
import fitz

class PDFdata:
    def __init__(self,filepath):
        self.filepath = filepath

        # Basic File Data
        self.data = None
        self.author = None
        self.creator = None
        self.producer = None
        self.title = None
        self.subject = None
        self.keywords = None
        self.page_count = None
        self.file_size = None

        # Text Data
        self.text = None
        self.word_count = None
        self.line_count = None
        self.char_count = None

        # Image Data
        self.image_count = 0
        self.images = []

        # Table Data
        self.table_count = 0
        self.tables = []

        # Link Data
        self.link_count = 0
        self.links = []
    
    def extract_pdf_data(self):
        try:
            self.file_size  = os.path.getsize(self.filepath)

            with plum.open(self.filepath) as pdf:

                self.extract_basic_data(pdf)
                self.extract_text_data(pdf)
                self.extract_table_data(pdf)

            with fitz.open(self.filepath) as doc:
                self.extract_image_data(doc)
                self.extract_hyperlinks(doc)

        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {self.filepath}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {self.filepath}")
        except Exception as e:
            raise Exception(f"Error analyzing PDF: {str(e)}")

    def extract_basic_data(self, pdf):
        self.data = pdf.metadata
        self.page_count = len(pdf.pages)

        if self.data:
            self.author = self.data.get('Author', 'Unknown')
            self.creator = self.data.get('Creator', 'Unknown')
            self.producer = self.data.get('Producer', 'Unknown')
            self.title = self.data.get('Title', 'Unknown')
            self.subject = self.data.get('Subject', 'Unknown')
            self.keywords = self.data.get('Keywords', 'Unknown')

    def extract_text_data(self, pdf):
        text_parts = []
        words = []
        
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
                words.extend(page_text.split())
        
        self.text = "\n".join(text_parts)
        self.word_count = len(words)
        self.char_count = len(self.text)
        self.line_count = self.text.count('\n')

    def extract_image_data(self,doc):
        for page_num, page in enumerate(doc, 1):
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
        
        self.image_count = len(self.images)
    
    def extract_table_data(self, pdf):
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            
            for table_idx, table in enumerate(tables, 1):
                self.tables.append({
                    'page': page_num,
                    'table_number': table_idx,
                    'data': table,
                    'rows': len(table),
                    'columns': len(table[0]) if table else 0
                })
        
        self.table_count = len(self.tables)

    def extract_hyperlinks(self, doc):
        for page_num, page in enumerate(doc, 1):
            links = page.get_links()
            
            for link in links:
                if 'uri' in link:
                    self.links.append({
                        'page': page_num,
                        'url': link['uri']
                    })
        
        self.link_count = len(self.links)

def main():
    filepath = r"C:\Users\brett\OneDrive\Desktop\COSC 499\capstone-project-team-10\tests\sample_files\499SamplePDF.pdf"

    pdf = PDFdata(filepath)
    pdf.extract_pdf_data()
    
    # Test the extraction
    print(f"Title: {pdf.title}")
    print(f"Author: {pdf.author}")
    print(f"Pages: {pdf.page_count}")
    print(f"Images: {pdf.image_count}")
    print(f"Tables: {pdf.table_count}")
    print(f"Links: {pdf.link_count}")
    print(f"Words: {pdf.word_count}")

if __name__ == "__main__":
    main()