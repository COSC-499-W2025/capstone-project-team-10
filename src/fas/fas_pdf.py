import os
import pdfplumber as plum
import fitz
from typing import Dict, Any

def extract_pdf_data(path: str) -> Dict[str, Any]:
    """
        Extracts data from PDF using pdfplumber library.
        Args:
            path (str): Path to the PDF file.
        Returns:
            metadata: dictionary holding all the extracted data
    """
    try:
        file_size = os.path.getsize(path)
            
        # Open documents with pdfplumber and pymupdf (fitz) and calls extraction methods
        with plum.open(path) as pdf_p, fitz.open(path) as pdf_f:

            basic_metadata = pdf_p.metadata or {}

            text_parts = []
            tables = []
            images = []
            hyperlinks = []
            word_count = 0

            # Iterate over each page with plumber
            for page_num, page in enumerate(pdf_p.pages, 1):

                # Extract text using plumber
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    # Split on whitespace and filter out single-character symbols
                    words = page_text.split()
                    filtered_words = [w for w in words if not (len(w) == 1 and not w.isalnum())]
                    word_count += len(filtered_words)
                
                # Extract tables using plumber
                page_tables = page.extract_tables()
                for table_idx, table in enumerate(page_tables, 1):
                    tables.append({
                        'page': page_num,
                        'table_number': table_idx,
                        'data': table,
                        'rows': len(table),
                        'columns': len(table[0]) if table and table[0] else 0
                    })

                # Get fitz page number from plumber page number
                page_fitz = pdf_f[page_num - 1]

                # Extract Images using fitz
                image_list = page_fitz.get_images()
                for img_idx, img in enumerate(image_list, 1):
                    xref = img[0]
                    try:
                        base_image = pdf_f.extract_image(xref)
                        images.append({
                            'page': page_num,
                            'image_number': img_idx,
                            'format': base_image.get("ext"),
                            'width': base_image.get("width"),
                            'height': base_image.get("height")
                        })
                    except Exception:
                        continue

                # Extracts links using fitz
                links = page_fitz.get_links()
                for link_idx, link in enumerate(links, 1):
                    if link.get('uri'):
                        hyperlinks.append({
                            'page': page_num,
                            'link_number': link_idx,
                            'url': link.get('uri'),
                            'type': link.get('type', 'unknown')
                        })

            text = "\n".join(text_parts)
            char_count = len(text)
            line_count = text.count('\n')
   
            metadata = {
                "file_path": path,
                "file_size_bytes": file_size,
                "pdf_metadata": basic_metadata,
                "text": text,
                "tables": tables,
                "images": images,
                "hyperlinks": hyperlinks,
                "counts": {
                    "pages": len(pdf_p.pages),
                    "words": word_count,
                    "characters": char_count,
                    "lines": line_count,
                    "tables": len(tables),
                    "images": len(images),
                    "hyperlinks": len(hyperlinks)
                }
            }
        return metadata

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {path}")
    except Exception as e:
        raise Exception(f"Error analyzing PDF: {str(e)}")