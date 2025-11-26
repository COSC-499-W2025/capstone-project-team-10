import sys

import pandas as pd
from typing import List
import os

class LogSorter:

    """
        Stores one singular log file, keeps them within an attribute
    """

    def __init__(self, path):

        self.__log_path = path
        self.log = pd.read_csv(self.__log_path)
        self.params = []
        self.ascending = []

    def set_sort_parameters(self, parameters: List[str], ascending: List[bool] = None):
        """
            Set sorting parameters for one or multiple columns

            Args:
                parameters: List of column names to sort by (size 1+)
                ascending: List of booleans for sort order, defaults to all True

            Raises:
                ValueError: If 'Extra data' column is included or columns don't exist
        """
        if not parameters:  # Checking for existence of parameters
            raise ValueError("Parameters list cannot be empty")

        if "Extra data" in parameters:  # Checking for if Extra data is mentioned as a paran
            raise ValueError("Cannot sort by 'Extra data' column - this column is disregarded")

        for param in parameters:
            if param not in self.log.columns:
                raise ValueError(f"Column '{param}' not found in log data. Available columns: {list(self.log.columns)}")

        if ascending is None: # Defaulter - everything to ascending
            ascending = [True] * len(parameters)

        if len(ascending) != len(parameters):
            raise ValueError(
                f"Number of order flags ({len(ascending)}) must match number of parameters ({len(parameters)})")

        self.params = parameters
        self.ascending = ascending

    def sort(self):
        """
            Sort the log data based on previously set parameters

            Returns:
                pd.DataFrame: Sorted dataframe

            Raises:
                ValueError: If no sorting parameters are set
        """
        if not self.params:
            raise ValueError("No sorting parameters set. Use set_sort_parameters() first.")

        # Perform the sort
        self.log = self.log.sort_values(by = self.params, ascending = self.ascending)
        return self.log

    def get_available_columns(self) -> List[str]:
        """
            Return list of available columns for sorting (excluding Extra data)
        """
        return [col for col in self.log.columns if col != "Extra data"]

    def get_preview(self, n: int = 5):
        """
            Show a preview of how the data will be sorted without modifying the original

            Args:
                n: Number of rows to preview

            Returns:
                pd.DataFrame: Preview of sorted data

            Raises:
                ValueError: If no sorting parameters are set
        """
        if not self.params:
            raise ValueError("No sorting parameters set. Use set_sort_parameters() first.")

        # Return preview without modifying original data
        return self.log.sort_values(by = self.params, ascending = self.ascending).head(n)

    def return_csv(self):
        """
            Returns the .csv
        """
        directory, filename = os.path.split(self.__log_path)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_sorted{ext}"
        new_path = os.path.join(directory, new_filename)

        self.log.to_csv(new_path, index = False)
        return self.log.to_csv(index = False)

    def get_sort_params(self):
        """
            Returns the sorting parameters
        """
        return {"Parameters": self.params, "Orders": self.ascending}

r"""
sorter = LogSorter(r"C:\Users\pqbao\AppData\Roaming\Capstone Project Team 10\logs\0.log")
print(sorter.get_available_columns())
sorter.set_sort_parameters(['Created time'], [True])
print(sorter.get_preview())
sorter.sort()
print(sorter.get_sort_params())
"""

