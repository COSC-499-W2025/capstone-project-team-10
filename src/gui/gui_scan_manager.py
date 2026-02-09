from src.fas.fas import FileAnalysis as fas
from src.fss.fss import FSS_Search, search

class ScanManager:
    
    def __init__(self):
        self.fss = None
        self.last_result = None
    
    def scan(self, directory_path, filters: dict):
        """
          Initiate scan on the given directory using provided filters.
        """
        search_params = FSS_Search(
            input_path=directory_path,
            excluded_path=filters.get('excluded_paths', set()),
            file_types=filters.get('file_types', set()),
            time_lower_bound=filters.get('time_lower_bound', None),
            time_upper_bound=filters.get('time_upper_bound', None),
        )
        self.last_result = search(search_params)
        return self.last_result
    
    def get_scan_results(self):
        """
          Retrieve last scan results (currently total files scanned).
        """
        return self.last_result