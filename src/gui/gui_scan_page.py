import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

class ScanPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ScanPage, self).__init__(parent)
        
        self.selected_directory = None
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.setSpacing(20)
        
        # Placeholder text
        self.title_label = QtWidgets.QLabel("Select files to scan")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Directory display label
        self.directory_label = QtWidgets.QLabel("No directory selected")
        self.directory_label.setAlignment(QtCore.Qt.AlignCenter)
        self.directory_label.setStyleSheet("font-size: 12px; color: gray;")
        self.layout.addWidget(self.directory_label)
        
        # Button container for centering
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Top button - Browse files
        self.browse_button = QtWidgets.QPushButton("Browse Files", self)
        self.browse_button.setFixedSize(200, 50)
        self.browse_button.clicked.connect(self.browse_files)
        button_layout.addWidget(self.browse_button, alignment=QtCore.Qt.AlignCenter)
        
        # Bottom button - Start scan
        self.scan_button = QtWidgets.QPushButton("Start Scan", self)
        self.scan_button.setFixedSize(200, 50)
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button, alignment=QtCore.Qt.AlignCenter)
        
        self.layout.addLayout(button_layout)
        self.layout.addStretch()
        
    def browse_files(self):
        file_dialog = QtWidgets.QFileDialog()
        selected_directory = file_dialog.getExistingDirectory(self, "Select a directory to scan")
        
        if selected_directory:
            self.selected_directory = selected_directory
            # Print to terminal
            print(f"Selected directory: {selected_directory}")
            # Display on GUI
            self.directory_label.setText(f"Directory: {selected_directory}")
        
    def start_scan(self):
        # TODO: Implement scan functionality
        pass