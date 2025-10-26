import os
from datetime import datetime

def analyze_pdf_file(filepath):
   with open(filepath, 'rb') as file:
        data = os.stat(file.fileno())

        # Basic PDF File Data
        print(f"Author: {data.st_dev}")
        print(f"File Size: {data.st_size} bytes")
        print(f"Date Last Accessed: {datetime.fromtimestamp(data.st_atime)}")
        print(f"Date Last Modified: {datetime.fromtimestamp(data.st_mtime)} ")
        print(f"Date Created: {datetime.fromtimestamp(data.st_ctime)}") 

        # PDF Content Data
        content = file.read()
        is_valid = content.startswith(b'%PDF-') and b'%%EOF' in content
        if(is_valid):
            version = content[5:8].decode('ascii', errors='ignore')
        else:
            version = "Unknown"

        if(b'/Image' in content):
            has_image = True
        else:
            has_image = False

        print(f"PDF Version: {version}")
        print(f"Number of Pages: {content.count(b'/Type/Page')}") 
        print(f"Content Size: {len(content)}")
        print(is_valid)

def main():
    filepath = r"C:\Users\brett\OneDrive\Desktop\COSC 499\capstone-project-team-10\tests\sample_files\499SamplePDF.pdf"
    filepath2 = r"C:\Users\brett\OneDrive\Desktop\COSC 499\capstone-project-team-10\tests\sample_files\Assignment4-1.pdf"

    analyze_pdf_file(filepath)
    print(" ")
    #analyze_pdf_file(filepath2)

if __name__ == "__main__":
    main()