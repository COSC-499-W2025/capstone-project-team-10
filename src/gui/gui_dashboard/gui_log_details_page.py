from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal
import csv
from src.fas.fas import FileAnalysis
import src.log.log as log

class ProjectFilesPage(QWidget):
    """Sub-page that displays all files belonging to a specific project."""
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()

        back_btn = QPushButton("← Back to Projects")
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
                background-color: #002145;
            }
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)

        self.title_label = QLabel("Project Files")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File Name", "File Type", "Created Time", "Importance"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 4):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    def load_project_files(self, project_id, files):
        self.title_label.setText(f"Files in Project: {project_id}")
        self.table.setRowCount(0)
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
            QTableWidget::item:selected {
                background-color: #002145;
                color: white;
            }
        """)

        # 'files' is expected to be a list of FileAnalysis objects from log.get_project()
        for idx, fa in enumerate(files):
            self.table.insertRow(idx)
            self.table.setItem(idx, 0, QTableWidgetItem(str(fa.file_name)))
            self.table.setItem(idx, 1, QTableWidgetItem(str(fa.file_type)))
            self.table.setItem(idx, 2, QTableWidgetItem(str(fa.created_time)))
            self.table.setItem(idx, 3, QTableWidgetItem(str(fa.importance)))


class LogDetailsPage(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, log_path=None, parent=None):
        super().__init__(parent)
        self.log_path = log_path
        self._project_ids = [] 
        self.setStyleSheet("background-color: white;")
        self.init_ui()
        if log_path:
            self.load_log_files()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)

        # --- Page 0: Project List ---
        self.projects_widget = QWidget()
        layout = QVBoxLayout(self.projects_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("background-color: #002145; color: white; padding: 8px; border-radius: 4px;")
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)

        self.title_label = QLabel("Log Details")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Project ID"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
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
            QTableWidget::item:selected {
                background-color: #002145;
                color: white;
            }
        """)
        
        # Connect the double-click to open the project
        self.table.cellDoubleClicked.connect(self.on_project_double_clicked)

        layout.addWidget(self.table)
        self.stack.addWidget(self.projects_widget)

        # --- Page 1: Per-Project File List ---
        self.project_files_page = ProjectFilesPage()
        # Wire the internal back button to return to index 0 (the list)
        self.project_files_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.project_files_page)

    def set_log_path(self, log_path):
        self.log_path = log_path
        if hasattr(self.log_path, 'name'):
            self.title_label.setText(f"Projects in: {self.log_path.name}")
        self.load_log_files()

    def load_log_files(self):
        self.table.setRowCount(0)
        self._project_ids = []
        projects = set()

        if not self.log_path or not self.log_path.exists():
            return

        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Get Project ID from the CSV column
                    pid = row.get("Project id", "").strip()
                    if pid and pid not in projects:
                        projects.add(pid)
                        self._project_ids.append(pid)

            for idx, pid in enumerate(self._project_ids):
                self.table.insertRow(idx)
                self.table.setItem(idx, 0, QTableWidgetItem(pid))

        except Exception as e:
            print(f"Error loading CSV: {e}")

    def on_project_double_clicked(self, row, _col):
        """Open the specific project view using log.get_project()."""
        project_id = self.table.item(row, 0).text()
        
        # Call the logic from src.log.log
        files = log.get_project(project_id)
        
        # Pass data to the sub-page and switch views
        self.project_files_page.load_project_files(project_id, files)
        self.stack.setCurrentIndex(1)