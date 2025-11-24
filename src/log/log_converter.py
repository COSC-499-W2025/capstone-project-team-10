import os
import pandas as pd
from tabulate import tabulate
from fpdf import FPDF

class LogConverter:
    """
        Storing both the paths and file contents
    """
    def __init__(self, path):
        self.__log_path = path
        self.csv = pd.read_csv(self.__log_path)
        self.headers = self.csv.columns.to_list()
        self.data = self.csv.to_dict(orient = 'records')

    def convert_to_JSON(self, output_path = None):
        """
            Convert (and appends) the converted log file in standard .JSON format
        """
        json_str = self.csv.to_json(orient = 'records', indent = 2)

        if output_path is None:
            base, _ = os.path.splitext(self.__log_path)
            output_path = f"{base}_converted.json"

        with open(output_path, "w") as f:
            f.write(json_str)

        return output_path

    def get_data_summary(self):
        """
            Return basic information about the data
        """
        return {
            'headers': self.headers,
            'row_count': len(self.csv),
            'column_count': len(self.headers),
            'data_types': self.csv.dtypes.to_dict()
        }

    def convert_to_md(self, output_path = None):
        """
            Convert to Markdown format with proper table formatting
        """

        if output_path is None:
            base, _ = os.path.splitext(self.__log_path)
            output_path = f"{base}_converted.md"

        md_table = tabulate(self.csv, headers = 'keys', tablefmt = 'github', showindex = False) # Read the doc for usage

        # Add a title and metadata
        md_content = f"# Log Data\n\n"
        md_content += f"**Source**: {os.path.basename(self.__log_path)}\n\n"
        md_content += f"**Headers**: {', '.join(self.headers)}\n\n"
        md_content += f"**Records**: {len(self.csv)}\n\n"
        md_content += "## Data Table\n\n"
        md_content += md_table

        with open(output_path, "w") as f:
            f.write(md_content)

        return output_path

    def __convert_to_pdf_test(self, output_path = None):

        """
            Convert to PDF (requires additional libraries)
            Note: This is an experimental method using reportlab - libraries are not imported and method is hidden (for reference)
            Only try to install libraries if triggered - otherwise not needed
            Experimental due to previous issues / libraries being janky
        """
        try:
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
        except ImportError:
            print("Please install reportlab: pip install reportlab")
            return None
        if output_path is None:
            base, _ = os.path.splitext(self.__log_path)
            output_path = f"{base}_converted.pdf"

        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize = landscape(letter))
        elements = []
        styles = getSampleStyleSheet()

        # Add title
        title = Paragraph(f"Log Data - {os.path.basename(self.__log_path)}", styles['Heading1'])
        elements.append(title)

        # Add metadata
        meta_text = f""
        meta = Paragraph(meta_text, styles['Normal'])
        elements.append(meta)

        # Convert DataFrame to list of lists for table
        table_data = [self.headers] + self.csv.values.tolist()

        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        doc.build(elements)

        return output_path

    def convert_to_pdf(self, output_path = None):

        """
            Convert to PDF using fpdf2 with enhanced table formatting
        """

        if output_path is None:
            base, _ = os.path.splitext(self.__log_path)
            output_path = f"{base}_converted.pdf"

        pdf = FPDF(orientation = 'L', unit = 'mm', format = 'A4')
        pdf.set_auto_page_break(auto = True, margin = 15)
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, f"Log Data - {os.path.basename(self.__log_path)}", 0, 1, 'C')

        # Metadata with proper spacing
        pdf.set_font("Helvetica", size = 12)

        # Table
        col_width = (pdf.w - 2 * pdf.l_margin) / len(self.headers)
        row_height = 10

        pdf.set_font("Helvetica", 'B', 11) # Header
        pdf.set_fill_color(200, 200, 200)

        for header in self.headers:
            pdf.cell(col_width, row_height, str(header), border = 1, align = 'C', fill = True)
        pdf.ln()

        # Rows
        pdf.set_font("Helvetica", size = 10)
        pdf.set_fill_color(255, 255, 255)  # White background
        fill = False

        for index, row in self.csv.iterrows():
            # Check for page break
            if pdf.get_y() + row_height > pdf.h - pdf.b_margin:
                pdf.add_page(orientation = 'L')
                pdf.set_font("Helvetica", 'B', 11)
                pdf.set_fill_color(200, 200, 200)
                for header in self.headers:
                    pdf.cell(col_width, row_height, str(header), border = 1, align = 'C', fill = True)
                pdf.ln()
                pdf.set_font("Helvetica", size = 10)
                pdf.set_fill_color(255, 255, 255)

            fill = not fill # Alternate colors
            if fill:
                pdf.set_fill_color(240, 240, 240)  # Light gray
            else:
                pdf.set_fill_color(255, 255, 255)  # White

            for item in row:
                pdf.cell(col_width, row_height, str(item), border = 1, align = 'L', fill = True)
            pdf.ln()

        pdf.output(output_path)
        return output_path