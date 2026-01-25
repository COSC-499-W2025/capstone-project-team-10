import pandas as pd
from pathlib import Path

class LogIteratorAddor:

    def __init__(self, log_path):
        """
        Initialize the LogIteratorAddor with a log file path.
        
        Args:
            log_path: Path to the .log (CSV) file
        """
        self.log_path = Path(log_path)
        self.df = pd.read_csv(log_path)
        self._current_index = 0
    
    def __iter__(self):
        self._current_index = 0
        return self
    
    def __next__(self):
        if self._current_index < len(self.df):
            r = self.df.iloc[self._current_index]
            self._current_index += 1
            return r
        else:
            raise StopIteration
    
    def add_row(self, row_data):
        """
            Add a new row to the DataFrame.
        
            Args:
                row_data: Dictionary with column names as keys
        """
        new_row = pd.DataFrame([row_data])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
    
    def add_rows(self, rows_data):
        """
            Add multiple rows to the DataFrame.

            Args:
                rows_data: List of dictionaries, each representing a row
        """
        new_rows = pd.DataFrame(rows_data)
        self.df = pd.concat([self.df, new_rows], ignore_index=True)
    
    def save(self, output_path=None):
        """
            Save the DataFrame back to the log file.

            Args:
                output_path: Optional path to save to. If None, overwrites the original file.
        """
        save_path = output_path if output_path else self.log_path
        self.df.to_csv(save_path, index=False)
    
    def __len__(self):
        """
            Return the number of rows in the DataFrame.
        """
        return len(self.df)
    
    def __getitem__(self, index):
        """
            Allow indexing to get rows.
        """
        return self.df.iloc[index]
    
# Sample code for the GUI developer
r"""
# Initialize
log = LogIteratorAddor(r"C:\Users\pqbao\AppData\Roaming\Capstone Project Team 10\logs\0.log") # Change this into the path of the log file that you want to test on

# Showing all the columns we can iterate from
print(list(log.df.columns))

# Iterating
for row in log:
    print(f"File: {row['File name']}, Type: {row['File type']}, Importance: {row['Importance']}") # Only showing the File name, File type and Importance

# Old len
print(len(log))

# Adding a row
log.add_row({
    'File path analyzed': 'C:\\Users\\pqbao\\test.py',
    'File name': 'test.py',
    'File type': 'py',
    'Last modified': '2026-01-24T10:00:00',
    'Created time': '2026-01-24T10:00:00',
    'Extra data': "{'language': 'python'}",
    'Importance': 15.0
})

# New len
print(len(log))

# Printing the last object
print(log[-1])

# Printing the first object
print(log[0])
"""
