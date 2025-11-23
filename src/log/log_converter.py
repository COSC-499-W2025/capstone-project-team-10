import os

import pandas as pd


class LogConverter:
    """
    Storing both the paths and file contents
    """

    def __init__(self, path):
        self.__log_path = path
        self.csv = pd.read_csv(self.__log_path)

    def convert_to_JSON(self):
        """
        Convert (and appends) the converted log file in standard .JSON format
        """
        json_str = self.csv.to_json(orient="records", indent=2)

        base, _ = os.path.splitext(self.__log_path)
        json_path = (
            f"{base}_converted.json"  # Differentiate the name, in case of funniness
        )

        with open(
            json_path,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(json_str)

        return json_path

    def convert_to_md(self):
        return None

    def convert_to_pdf(self):
        return None
