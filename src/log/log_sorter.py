import pandas as pd
from typing import List

class LogSorter:

    """
        Stores one singular log file, keeps them within an attribute
    """

    def __init__(self, path):

        self.__log_path = path
        self.log = pd.read_csv(self.__log_path)
        self.params = []
        self.orders = []
        
    def set_sort_parameters(self, parameters: List[str], orders: List[str] = None):
        """
            Set sorting parameters for multiple columns

            Args:
                parameters: List of column names to sort by (can be single element)
                orders: List of orders ('ascending'/'descending'), defaults to all ascending

            Raises:
                ValueError: If 'Extra data' column is included or columns don't exist
        """
        if not parameters:
            raise ValueError("Parameters list cannot be empty")

        if "Extra data" in parameters:
            raise ValueError("Cannot sort by 'Extra data' column - this column is disregarded")

        for param in parameters:
            if param not in self.log.columns:
                raise ValueError(f"Column '{param}' not found in log data. Available columns: {list(self.log.columns)}")

        if orders is None:
            orders = ["ascending"] * len(parameters)

        valid_orders = ["ascending", "descending"]
        for order in orders:
            if order not in valid_orders:
                raise ValueError(f"Order must be 'ascending' or 'descending', got '{order}'")

        if len(orders) != len(parameters):
            raise ValueError(f"Number of orders ({len(orders)}) must match number of parameters ({len(parameters)})")

        self.params = parameters
        self.orders = orders

    def sort(self):

         return None
