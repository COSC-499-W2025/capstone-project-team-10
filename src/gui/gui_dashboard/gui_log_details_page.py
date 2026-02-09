from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
import csv
from src.fas.fas import FileAnalysis

class LogDetailsPage(QWidget):
    back_clicked = pyqtSignal()
    
    def __init__(self, log_path=None, parent=None):
        super().__init__(parent)
        self.log_path = log_path
        self.projects = {}
        self.setStyleSheet("background-color: white;")
        self.init_ui()
        if log_path:
            self.load_log_files()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #002145;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)
        
        self.title_label = QLabel("Log Details")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File Name", "File Type", "Created Time", "Importance"])
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e0e0e0;
                border: none;
                color: black; 
            }
            QHeaderView::section {
                background-color: white;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: normal;
                color: #666;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
                color: black; 
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.table)
    
    def set_log_path(self, log_path):
        # Set the log path and load its contents
        self.log_path = log_path
        self.title_label.setText(f"Files in: {self.log_path.name}")
        self.load_log_files()
    
    def load_log_files(self):
        # Read the log file and fill the table with file entries
        self.table.setRowCount(0)  # Clear existing rows
        self.projects.clear()  # Clear previous data
        
        if not self.log_path or not self.log_path.exists():
            print(f"Log path does not exist: {self.log_path}")
            return
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    fa = FileAnalysis(
                        row.get("File path analyzed", ""),
                        row.get("File name", ""),
                        row.get("File type", ""),
                        row.get("Last modified", ""),
                        row.get("Created time", ""),
                        row.get("Extra data", ""),
                        row.get("Importance", ""),
                        row.get("Customized", ""),
                    )
                    self.projects[fa.file_name] = fa

            for idx, (file_name, fa) in enumerate(self.projects.items()):
                self.table.insertRow(idx)
                self.table.setItem(idx, 0, QTableWidgetItem(fa.file_name))
                self.table.setItem(idx, 1, QTableWidgetItem(fa.file_type))
                self.table.setItem(idx, 2, QTableWidgetItem(fa.created_time))
                self.table.setItem(idx, 3, QTableWidgetItem(fa.importance))
                
        except FileNotFoundError:
            print(f"Log file not found: {self.log_path}")
        except csv.Error as e:
            print(f"CSV error reading log file: {e}")
        except Exception as e:
            print(f"Error loading log file: {e}")
            import traceback
            traceback.print_exc()