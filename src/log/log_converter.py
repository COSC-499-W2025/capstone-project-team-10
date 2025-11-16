import os
import pandas as pd

class LogConverter:

    def __init__(self, path):
        self.__log_path = path
        self.csv = pd.read_csv(self.__log_path)

    def convert_to_JSON(self):
        json_str = self.csv.to_json(orient='records', indent=2)

        # "file.csv" → "file_converted.json"
        base, _ = os.path.splitext(self.__log_path)
        json_path = f"{base}_converted.json"

        with open(json_path, "w") as f:
            f.write(json_str)

        return json_path  # location of converted file

    def convert_to_md(self):
        return None

    def convert_to_pdf(self):
        return None
