import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from datetime import datetime

class FilterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(FilterDialog, self).__init__(parent)
        
        self.setWindowTitle("Scan Filters")
        self.setFixedSize(500, 600)
        
        self.excluded_paths = set()
        self.file_types = set()
        self.time_lower_bound = None
        self.time_upper_bound = None
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Time bounds section
        time_group = QtWidgets.QGroupBox("Time Bounds")
        time_layout = QtWidgets.QFormLayout()
        
        self.lower_bound_edit = QtWidgets.QDateTimeEdit()
        self.lower_bound_edit.setCalendarPopup(True)
        self.lower_bound_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.lower_bound_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        
        self.upper_bound_edit = QtWidgets.QDateTimeEdit()
        self.upper_bound_edit.setCalendarPopup(True)
        self.upper_bound_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.upper_bound_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        
        time_layout.addRow("Start Time:", self.lower_bound_edit)
        time_layout.addRow("End Time:", self.upper_bound_edit)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # Excluded directories section
        exclude_group = QtWidgets.QGroupBox("Excluded Directories")
        exclude_layout = QtWidgets.QVBoxLayout()
        
        self.exclude_list = QtWidgets.QListWidget()
        exclude_layout.addWidget(self.exclude_list)
        
        exclude_btn_layout = QtWidgets.QHBoxLayout()
        self.add_exclude_btn = QtWidgets.QPushButton("Add Directory")
        self.add_exclude_btn.setAutoDefault(False)  # Add this line
        self.add_exclude_btn.clicked.connect(self.add_excluded_directory)
        self.remove_exclude_btn = QtWidgets.QPushButton("Remove")
        self.remove_exclude_btn.setAutoDefault(False)  # Add this line
        self.remove_exclude_btn.clicked.connect(self.remove_excluded_directory)
        
        exclude_btn_layout.addWidget(self.add_exclude_btn)
        exclude_btn_layout.addWidget(self.remove_exclude_btn)
        exclude_layout.addLayout(exclude_btn_layout)
        
        exclude_group.setLayout(exclude_layout)
        layout.addWidget(exclude_group)
        
        # File types section
        filetype_group = QtWidgets.QGroupBox("File Types")
        filetype_layout = QtWidgets.QVBoxLayout()
        
        self.filetype_list = QtWidgets.QListWidget()
        filetype_layout.addWidget(self.filetype_list)
        
        filetype_input_layout = QtWidgets.QHBoxLayout()
        self.filetype_input = QtWidgets.QLineEdit()
        self.filetype_input.setPlaceholderText("e.g., .py, .txt, .cpp")
        self.filetype_input.returnPressed.connect(self.add_file_type)  # Add this line
        self.add_filetype_btn = QtWidgets.QPushButton("Add")
        self.add_filetype_btn.clicked.connect(self.add_file_type)
        self.remove_filetype_btn = QtWidgets.QPushButton("Remove")
        self.remove_filetype_btn.clicked.connect(self.remove_file_type)
        
        filetype_input_layout.addWidget(self.filetype_input)
        filetype_input_layout.addWidget(self.add_filetype_btn)
        filetype_input_layout.addWidget(self.remove_filetype_btn)
        filetype_layout.addLayout(filetype_input_layout)
        
        filetype_group.setLayout(filetype_layout)
        layout.addWidget(filetype_group)
        
        # Dialog buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.apply_btn = QtWidgets.QPushButton("Apply Filters")
        self.apply_btn.setDefault(False)  # Add this line
        self.apply_btn.clicked.connect(self.accept)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setDefault(False)  # Add this line
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
    def add_excluded_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory to Exclude")
        if directory:
            self.excluded_paths.add(directory)
            self.exclude_list.addItem(directory)
    
    def remove_excluded_directory(self):
        current_item = self.exclude_list.currentItem()
        if current_item:
            self.excluded_paths.remove(current_item.text())
            self.exclude_list.takeItem(self.exclude_list.row(current_item))
    
    def add_file_type(self):
        file_type = self.filetype_input.text().strip()
        if file_type:
            if not file_type.startswith('.'):
                file_type = '.' + file_type
            self.file_types.add(file_type)
            self.filetype_list.addItem(file_type)
            self.filetype_input.clear()
    
    def remove_file_type(self):
        current_item = self.filetype_list.currentItem()
        if current_item:
            self.file_types.remove(current_item.text())
            self.filetype_list.takeItem(self.filetype_list.row(current_item))
    
    def get_filters(self):
        """Returns the configured filters"""
        self.time_lower_bound = self.lower_bound_edit.dateTime().toPyDateTime()
        self.time_upper_bound = self.upper_bound_edit.dateTime().toPyDateTime()
        
        return {
            'excluded_paths': self.excluded_paths,
            'file_types': self.file_types,
            'time_lower_bound': self.time_lower_bound,
            'time_upper_bound': self.time_upper_bound
        }