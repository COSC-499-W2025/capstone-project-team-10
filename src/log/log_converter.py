import os
import pandas as pd
from tabulate import tabulate

class LogConverter:
    """
        Storing both the paths and file contents
    """
    def __init__(self, path):
        self.__log_path = path
        self.csv = pd.read_csv(self.__log_path)
        self.headers = self.csv.columns.to_list()
        self.data = self.csv.to_dict(orient='records')

    def convert_to_JSON(self):
        """
            Convert (and appends) the converted log file in standard .JSON format
        """
        json_str = self.csv.to_json(orient='records', indent=2)

        base, _ = os.path.splitext(self.__log_path)
        json_path = f"{base}_converted.json" # Differentiate the name, in case of funniness

        with open(json_path, "w") as f:
            f.write(json_str)

        return json_path

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

    def convert_to_md(self, output_path=None):
        """
        Convert to Markdown format with proper table formatting
        """
        if output_path is None:
            base, _ = os.path.splitext(self.__log_path)
            output_path = f"{base}_converted.md"

        # Using tabulate for better markdown table formatting
        md_table = tabulate(self.csv, headers='keys', tablefmt='github', showindex=False)

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

    def convert_to_pdf(self):
        return None


convert_test = LogConverter(r"C:\Users\pqbao\AppData\Roaming\Capstone Project Team 10\logs\0.log")
convert_test.convert_to_md()
# convert_test.convert_to_JSON()
print(convert_test.headers)
print(convert_test.data)