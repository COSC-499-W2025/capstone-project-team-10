from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QLineEdit, QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

from pathlib import Path
from src.gui.gui_resume_manager import ResumeManager
from src.gui.gui_items_page.gui_items_helper import append_generated_item
from src.gui.gui_skills_page import SkillsPage


class PortfolioPage(QWidget):
    """
    GUI page for editing the Portfolio.
    """

    def __init__(self):
        super().__init__()

        self.manager = ResumeManager()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # --- Left Panel (Log + Projects) ---

        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        # --- Log chooser UI ---
        log_row = QHBoxLayout()
        log_row.setSpacing(8)

        self.log_label = QLabel("Current log:")
        self.log_path_label = QLabel(str(self.manager.log_file))
        self.log_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.choose_log_btn = QPushButton("Choose Log...")
        self.choose_log_btn.clicked.connect(self.choose_log_file)

        log_row.addWidget(self.log_label)
        log_row.addWidget(self.choose_log_btn)
        left_panel.addLayout(log_row)
        left_panel.addWidget(self.log_path_label)

        # --- Project list ---
        self.project_list = QListWidget()
        self.project_list.addItems(self.manager.projects.keys())
        self.project_list.currentTextChanged.connect(self.load_project)

        left_panel.addWidget(QLabel("Projects:"))
        left_panel.addWidget(self.project_list, 1)

        # Put left panel into a QWidget so we can add it to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        layout.addWidget(left_widget, 1)

        # --- Right Panel (Editor) ---
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
        editor_layout.addWidget(self.extra_data_edit, 1)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        
        self.skills_page_btn = QPushButton("View Skills")
        self.skills_page_btn.clicked.connect(self.open_skills_page)

        btn_layout.addWidget(self.skills_page_btn)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)

        self.generate_portfolio_btn = QPushButton("Generate Portfolio")
        self.generate_portfolio_btn.clicked.connect(self.generate_portfolio)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.generate_portfolio_btn)

        editor_layout.addLayout(btn_layout)

        editor_widget = QWidget()
        editor_widget.setLayout(editor_layout)
        layout.addWidget(editor_widget, 3)

        # Track currently selected project
        self.current_project_name: str = ""

    # --- Log choosing / reloading ---
    def choose_log_file(self):
        """
        Let user pick a CSV log file and reload the ResumeManager.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a log file",
            "",
            "Log Files (*.log);;All Files (*)"
        )

        if not file_path:
            return

        chosen = Path(file_path)
        if not chosen.exists():
            QMessageBox.warning(self, "Invalid file", "That file does not exist.")
            return

        # Reload manager using chosen log
        self.manager = ResumeManager(log_file=chosen)
        self.log_path_label.setText(str(self.manager.log_file))

        # Refresh list + clear editor
        self.refresh_project_list()
        self.clear_editor()

    def refresh_project_list(self):
        self.project_list.blockSignals(True)
        self.project_list.clear()
        self.project_list.addItems(self.manager.projects.keys())
        self.project_list.blockSignals(False)

        # Reset current selection
        self.current_project_name = ""

    def clear_editor(self):
        self.name_edit.clear()
        self.file_type_edit.clear()
        self.created_time_edit.clear()
        self.last_modified_edit.clear()
        self.extra_data_edit.clear()

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
        # self.extra_data_edit.setText(fa.extra_data)
        self.extra_data_edit.setText(self.manager.get_key_skills_csv(project_name))


    def save_changes(self):
        """Save current edits back to the ResumeManager (and log)."""
        if not self.current_project_name:
            return

        mods = {
            "file_name": self.name_edit.text(),
            "file_type": self.file_type_edit.text(),
            "created_time": self.created_time_edit.text(),
            "last_modified": self.last_modified_edit.text(),
            # "extra_data": self.extra_data_edit.toPlainText(),
        }

        self.manager.update_project_info(self.current_project_name, mods)
        
        self.manager.set_key_skills_from_csv(
            self.current_project_name,
            self.extra_data_edit.toPlainText()
        )

        # Refresh project list in case name changed
        self.refresh_project_list()

    def generate_portfolio(self):
        """Generate full portfolio using current project data."""
        pdf_path = self.manager.get_full_portfolio()
        if pdf_path:
            append_generated_item(pdf_path, "portfolio", self.manager.log_file)
            print(f"Portfolio PDF generated at: {pdf_path}")

        if not pdf_path:
            QMessageBox.warning(self, "Error", "Failed to generate portfolio.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Portfolio Generated")
        msg.setText("Portfolio generated successfully!")
        msg.setInformativeText(str(pdf_path))
        open_btn = msg.addButton("Open Folder", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Ok)

        msg.exec_()

        if msg.clickedButton() == open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path.parent)))

    def open_skills_page(self):
        self.skills_page = SkillsPage(self.manager)
        self.skills_page.show()
