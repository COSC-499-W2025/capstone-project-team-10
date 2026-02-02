import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from src.gui.gui_scan_manager import ScanManager
from src.gui.gui_scan_filtering import FilterDialog

class ScanPage(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(ScanPage, self).__init__(parent)
        
        self.scan_manager = ScanManager()
        self.selected_directory = None
        self.current_filters = None
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.setSpacing(20)
        
        self.layout.addStretch()
        
        # Title
        self.title_label = QtWidgets.QLabel("File Analysis Scan")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Directory label
        self.directory_label = QtWidgets.QLabel("No directory selected")
        self.directory_label.setAlignment(QtCore.Qt.AlignCenter)
        self.directory_label.setStyleSheet("font-size: 12px; color: gray;")
        self.layout.addWidget(self.directory_label)
        
        # Button container for centering
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Button 1 - Choose directory
        self.browse_button = QtWidgets.QPushButton("Choose Directory", self)
        self.browse_button.setFixedSize(200, 50)
        self.browse_button.clicked.connect(self.browse_files)
        button_layout.addWidget(self.browse_button, alignment=QtCore.Qt.AlignCenter)
        
        # Button 2 - Choose filters
        self.filter_button = QtWidgets.QPushButton("Choose Filters", self)
        self.filter_button.setFixedSize(200, 50)
        self.filter_button.clicked.connect(self.open_filter_dialog)
        button_layout.addWidget(self.filter_button, alignment=QtCore.Qt.AlignCenter)
        
        # Button 3 - Start scan
        self.scan_button = QtWidgets.QPushButton("Start Scan", self)
        self.scan_button.setFixedSize(200, 50)
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button, alignment=QtCore.Qt.AlignCenter)
        
        self.layout.addLayout(button_layout)
        self.layout.addStretch()
        
        # Filter summary section (initially hidden)
        self.filter_summary = QtWidgets.QLabel()
        self.filter_summary.setAlignment(QtCore.Qt.AlignCenter)
        self.filter_summary.setStyleSheet("font-size: 10px; color: blue;")
        self.filter_summary.setVisible(False)
        self.layout.addWidget(self.filter_summary)
        
    def browse_files(self):
        file_dialog = QtWidgets.QFileDialog()
        selected_directory = file_dialog.getExistingDirectory(self, "Select a directory to scan")
        
        if selected_directory:
            self.selected_directory = selected_directory
            # Display on GUI
            self.directory_label.setText(f"Directory: {selected_directory}")
    
    def open_filter_dialog(self):
        """Open the filter dialog"""
        filter_dialog = FilterDialog(self)
        if filter_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.current_filters = filter_dialog.get_filters()
            self.display_filters(self.current_filters)
        
    def start_scan(self):
        if not self.selected_directory:
            QtWidgets.QMessageBox.warning(self, "No Directory", "Please select a directory first.")
            return
        
        if self.current_filters is None:
            QtWidgets.QMessageBox.warning(self, "No Filters", "Please choose filters first.")
            return
        
        # TODO: Pass filters and directory to scan_manager
        QtWidgets.QMessageBox.information(self, "Scan Started", f"Scanning {self.selected_directory} with filters applied.")
    
    def display_filters(self, filters):
        """Display the applied filters"""
        summary = "Applied Filters:\n"
        
        # File types
        if filters['file_types']:
            summary += f"File Types: {', '.join(filters['file_types'])}\n"
        else:
            summary += "File Types: None\n"
        
        # Excluded paths
        if filters['excluded_paths']:
            summary += f"Excluded Paths: {len(filters['excluded_paths'])} path(s)\n"
        else:
            summary += "Excluded Paths: None\n"
        
        # Time bounds
        if filters['time_lower_bound'] or filters['time_upper_bound']:
            lower = filters['time_lower_bound'].strftime("%Y-%m-%d %H:%M:%S") if filters['time_lower_bound'] else "None"
            upper = filters['time_upper_bound'].strftime("%Y-%m-%d %H:%M:%S") if filters['time_upper_bound'] else "None"
            summary += f"Time Bounds: {lower} to {upper}"
        else:
            summary += "Time Bounds: None"
        
        self.filter_summary.setText(summary)
        self.filter_summary.setVisible(True)