import pandas as pd

class LogSorter:

    """
        Stores one singular log file, keeps them within an attribute
    """

    def __init__(self, path):

        self.__log_path = path
        self.log = pd.read_csv(self.__log_path)
        self.param = ""
        self.order = "a"

    def accepts_param(self, prm, ordr):

        if prm not in self.log.columns:
            raise ValueError(f"Value '{prm}' does not exist in the log file")

        if ordr not in ["asc", "des"]:
            raise ValueError(f"Please choose a proper ordering : asc for Ascending or des for Descending")

        self.param = prm
        self.order = ordr

    def sort(self):
         
         return None
