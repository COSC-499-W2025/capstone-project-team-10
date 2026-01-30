# src/gui/resume_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt
from pathlib import Path
from src.gui.gui_resume_manager import ResumeManager


class ResumePage(QWidget):
    """
    GUI page for editing the Resume.
    """

    def __init__(self):
        super().__init__()
        self.manager = ResumeManager()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # --- Project list ---
        self.project_list = QListWidget()
        self.project_list.addItems(self.manager.projects.keys())
        self.project_list.currentTextChanged.connect(self.load_project)
        layout.addWidget(self.project_list, 1)

        # --- Editor panel ---
        editor_layout = QVBoxLayout()
        editor_layout.setSpacing(10)

        self.name_edit = QLineEdit()
        self.file_type_edit = QLineEdit()
        self.last_modified_edit = QLineEdit()
        self.created_time_edit = QLineEdit()
        self.extra_data_edit = QTextEdit()

        editor_layout.addWidget(QLabel("Project Name:"))
        editor_layout.addWidget(self.name_edit)
        editor_layout.addWidget(QLabel("File Type:"))
        editor_layout.addWidget(self.file_type_edit)
        editor_layout.addWidget(QLabel("Created Time:"))
        editor_layout.addWidget(self.created_time_edit)
        editor_layout.addWidget(QLabel("Last Modified:"))
        editor_layout.addWidget(self.last_modified_edit)
        editor_layout.addWidget(QLabel("Extra Data:"))
        editor_layout.addWidget(self.extra_data_edit)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        self.generate_pdf_btn = QPushButton("Generate Resume PDF")
        self.generate_pdf_btn.clicked.connect(self.generate_pdf)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.generate_pdf_btn)

        editor_layout.addLayout(btn_layout)
        layout.addLayout(editor_layout, 3)

        # Track currently selected project
        self.current_project_name: str = ""

    def load_project(self, project_name: str):
        """Load project data into editor."""
        self.current_project_name = project_name
        fa = self.manager.get_project_info(project_name)
        if not fa:
            return
        self.name_edit.setText(fa.file_name)
        self.file_type_edit.setText(fa.file_type)
        self.created_time_edit.setText(fa.created_time)
        self.last_modified_edit.setText(fa.last_modified)
        self.extra_data_edit.setText(fa.extra_data)

    def save_changes(self):
        """Save current edits back to the ResumeManager (and log)."""
        if not self.current_project_name:
            return
        mods = {
            "file_name": self.name_edit.text(),
            "file_type": self.file_type_edit.text(),
            "created_time": self.created_time_edit.text(),
            "last_modified": self.last_modified_edit.text(),
            "extra_data": self.extra_data_edit.toPlainText(),
        }
        self.manager.update_project_info(self.current_project_name, mods)
        # Refresh project list in case name changed
        self.project_list.clear()
        self.project_list.addItems(self.manager.projects.keys())

    def generate_pdf(self):
        """Generate full resume PDF using current project data."""
        pdf_path = self.manager.get_full_resume_pdf()
        if pdf_path:
            print(f"Resume PDF generated at: {pdf_path}")
