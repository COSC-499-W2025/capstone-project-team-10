import os
import pdfplumber as plum
from datetime import datetime

class PDFdata:
    def __init__(self,filepath):
        self.filepath = filepath

        # PDF File Data
        self.data = None
        self.author = None
        self.creator = None
        self.producer = None
        self.page_count = None
        self.text = None
        self.has_images = False
    
    def extract_pdf_data(self):
        try:
            with plum.open(self.filepath) as pdf:
                self.data = pdf.metadata

                if self.data:
                    self.author = self.data.get('Author', 'Unknown')
                    self.creator = self.data.get('Creator', 'Unknown')
                    self.producer = self.data.get('Producer', 'Unknown')

                self.page_count = len(pdf.pages)

                self.text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        self.text += page_text + "\n"
                
                self.has_images = False
                for page in pdf.pages:
                    if page.images:
                        self.has_images = True
                        break

        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {self.filepath}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {self.filepath}")
        except Exception as e:
            raise Exception(f"Error analyzing PDF: {str(e)}")

def main():
    filepath = r"C:\Users\brett\OneDrive\Desktop\COSC 499\capstone-project-team-10\tests\sample_files\499SamplePDF.pdf"
    filepath2 = r"C:\Users\brett\OneDrive\Desktop\COSC 499\capstone-project-team-10\tests\sample_files\Assignment4-1.pdf"

    pdf1 = PDFdata(filepath)
    pdf1.extract_pdf_data()
    
    # Test the extraction
    print(f"Author: {pdf1.author}")

    print(f"Pages: {pdf1.page_count}")
    print(f"Has images: {pdf1.has_images}")

    print(f"Text Content: {pdf1.text}")

if __name__ == "__main__":
    main()