from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QFileDialog,
    QMessageBox, QCheckBox, QSpinBox, QScrollArea, QInputDialog
)
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from pathlib import Path
from src.gui.gui_skills_page import SkillsPage
from src.gui.gui_resume_manager import ResumeManager

class ResumePage(QWidget):
    """
    GUI page for editing and customizing the Resume.
    Only shows Project files and their aggregated skills.
    Supports project re-ranking, chronology correction,
    skill highlighting, and showcase selection.
    """

    def __init__(self):
        super().__init__()
        self.manager = ResumeManager()
        self.current_project_name = ""

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # ---------------- Left Panel ----------------
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        # Log file chooser
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

        # Project list (drag/drop for re-ranking)
        self.project_list = QListWidget()
        self.project_list.setDragDropMode(QListWidget.InternalMove)
        self.project_list.currentTextChanged.connect(self.load_project)
        left_panel.addWidget(QLabel("Projects:"))
        left_panel.addWidget(self.project_list, 1)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        layout.addWidget(left_widget, 1)

        # ---------------- Right Panel ----------------
        editor_layout = QVBoxLayout()
        editor_layout.setSpacing(10)

        # Basic Project Info
        self.name_edit = QLineEdit()
        self.file_type_edit = QLineEdit()
        self.created_time_edit = QLineEdit()
        self.last_modified_edit = QLineEdit()
        # self.importance_edit = QSpinBox()
        # self.importance_edit.setRange(0, 100)
        self.customized_checkbox = QCheckBox("Customized")
        self.showcase_checkbox = QCheckBox("Include in Showcase")
        self.rank_spinbox = QSpinBox()
        self.rank_spinbox.setRange(0, 1000)

        editor_layout.addWidget(QLabel("Project Name:"))
        editor_layout.addWidget(self.name_edit)
        editor_layout.addWidget(QLabel("File Type:"))
        editor_layout.addWidget(self.file_type_edit)
        editor_layout.addWidget(QLabel("Created Time:"))
        editor_layout.addWidget(self.created_time_edit)
        editor_layout.addWidget(QLabel("Last Modified:"))
        editor_layout.addWidget(self.last_modified_edit)
        # editor_layout.addWidget(QLabel("Importance:"))
        # editor_layout.addWidget(self.importance_edit)
        editor_layout.addWidget(self.customized_checkbox)
        editor_layout.addWidget(QLabel("Project Rank:"))
        editor_layout.addWidget(self.rank_spinbox)
        editor_layout.addWidget(self.showcase_checkbox)

        # ---------------- Skills ----------------
        editor_layout.addWidget(QLabel("Aggregated Skills (all files):"))
        self.agg_skills_container = QVBoxLayout()
        agg_scroll = QScrollArea()
        agg_scroll.setWidgetResizable(True)
        agg_widget = QWidget()
        agg_widget.setLayout(self.agg_skills_container)
        agg_scroll.setWidget(agg_widget)
        editor_layout.addWidget(agg_scroll)

        add_agg_btn = QPushButton("+ Add Skill")
        add_agg_btn.clicked.connect(self.add_aggregate_skill)
        editor_layout.addWidget(add_agg_btn)

        editor_layout.addWidget(QLabel("Highlighted Skills (for Resume/Showcase):"))
        self.highlight_skills_container = QVBoxLayout()
        highlight_scroll = QScrollArea()
        highlight_scroll.setWidgetResizable(True)
        highlight_widget = QWidget()
        highlight_widget.setLayout(self.highlight_skills_container)
        highlight_scroll.setWidget(highlight_widget)
        editor_layout.addWidget(highlight_scroll)

        add_highlight_btn = QPushButton("+ Add Highlighted Skill")
        add_highlight_btn.clicked.connect(self.add_highlighted_skill)
        editor_layout.addWidget(add_highlight_btn)

        # Buttons
        btn_layout = QHBoxLayout()
        self.skills_page_btn = QPushButton("View Skills")
        self.skills_page_btn.clicked.connect(self.open_skills_page)
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        self.generate_resume_btn = QPushButton("Generate Resume PDF")
        self.generate_resume_btn.clicked.connect(self.generate_resume)
        btn_layout.addWidget(self.skills_page_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.generate_resume_btn)
        self.generate_portfolio_btn = QPushButton("Generate Portfolio")
        self.generate_portfolio_btn.clicked.connect(self.generate_portfolio)
        btn_layout.addWidget(self.generate_portfolio_btn)
        editor_layout.addLayout(btn_layout)

        editor_widget = QWidget()
        editor_widget.setLayout(editor_layout)
        layout.addWidget(editor_widget, 3)

        self.refresh_project_list()

    # ---------------- Log File ----------------
    def choose_log_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose a log file", "", "Log Files (*.log);;All Files (*)"
        )
        if not file_path:
            return
        chosen = Path(file_path)
        if not chosen.exists():
            QMessageBox.warning(self, "Invalid file", "That file does not exist.")
            return

        print(f"[ResumePage] User selected new log: {chosen}")

        # Clear GUI first
        self.current_project_name = ""
        self.clear_editor()
        self.project_list.clear()

        # Load new log
        self.manager = ResumeManager(log_file=chosen)

        self.log_path_label.setText(str(self.manager.log_file))
        self.refresh_project_list()
    # ---------------- Project List ----------------
    def refresh_project_list(self):
        self.project_list.blockSignals(True)
        self.project_list.clear()  

        projects_sorted = sorted(
            self.manager.projects.values(),
            key=lambda x: self.manager.get_project_extra_attributes(x.file_name).get("rank", 0)
        )

        for proj in projects_sorted:
            self.project_list.addItem(proj.file_name)

        self.project_list.blockSignals(False)
        self.current_project_name = ""

    # ---------------- Editor ----------------
    def clear_editor(self):
        self.name_edit.clear()
        self.file_type_edit.clear()
        self.created_time_edit.clear()
        self.last_modified_edit.clear()
        # self.importance_edit.setValue(0)
        self.customized_checkbox.setChecked(False)
        self.rank_spinbox.setValue(0)
        self.showcase_checkbox.setChecked(False)
        self.clear_skill_lists()

    def clear_skill_lists(self):
        # Clear aggregate skills
        for i in reversed(range(self.agg_skills_container.count())):
            widget = self.agg_skills_container.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Clear highlighted skills
        for i in reversed(range(self.highlight_skills_container.count())):
            widget = self.highlight_skills_container.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def load_project(self, project_name: str):
        self.current_project_name = project_name
        fa = self.manager.get_project_info(project_name)
        if not fa:
            return
        self.name_edit.setText(fa.file_name)
        self.file_type_edit.setText(fa.file_type)
        self.created_time_edit.setText(fa.created_time)
        self.last_modified_edit.setText(fa.last_modified)
        # self.importance_edit.setValue(int(float(fa.importance or 0)))
        self.customized_checkbox.setChecked(str(fa.customized).lower() == "true")

        extra = self.manager.get_project_extra_attributes(project_name)
        self.rank_spinbox.setValue(extra.get("rank", 0))
        self.showcase_checkbox.setChecked(bool(extra.get("showcase", False)))

        # Aggregate skills
        self.clear_skill_lists()
        agg_skills = self.manager.get_project_skills(project_name)
        for s in agg_skills:
            self.add_aggregate_skill_row(s)

        # Highlighted skills
        highlight_skills = extra.get("highlighted_skills", [])
        for s in highlight_skills:
            self.add_highlight_skill_row(s)

    # ---------------- Skill Rows ----------------
    def add_aggregate_skill_row(self, skill_name: str):
        row = QHBoxLayout()
        label = QLabel(skill_name)
        remove_btn = QPushButton("-")
        remove_btn.setMaximumWidth(30)
        remove_btn.setFixedHeight(20)
        remove_btn.setStyleSheet("padding: 0px; margin: 0px;")
        remove_btn.clicked.connect(lambda: self.remove_aggregate_skill(row, skill_name))
        row.addWidget(label)
        row.addWidget(remove_btn)
        container = QWidget()
        container.setLayout(row)
        self.agg_skills_container.addWidget(container)

    def add_highlight_skill_row(self, skill_name: str):
        row = QHBoxLayout()
        label = QLabel(skill_name)
        remove_btn = QPushButton("-")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_highlight_skill(row, skill_name))
        row.addWidget(label)
        row.addWidget(remove_btn)
        container = QWidget()
        container.setLayout(row)
        self.highlight_skills_container.addWidget(container)

    # ---------------- Skill Add / Remove ----------------
    def add_aggregate_skill(self):
        text, ok = QInputDialog.getText(self, "Add Aggregate Skill", "Skill Name:")
        if ok and text.strip():
            skill = text.strip()
            self.add_aggregate_skill_row(skill)

    def remove_aggregate_skill(self, row, skill_name):
        # row is a QHBoxLayout inside a QWidget
        container = row.parentWidget()  # get the QWidget that holds this row
        if container:
            self.agg_skills_container.removeWidget(container)
            container.setParent(None)

    def add_highlighted_skill(self):
        # Show only skills that exist in aggregate
        agg_skills = [self.agg_skills_container.itemAt(i).widget().layout().itemAt(0).widget().text()
                      for i in range(self.agg_skills_container.count())]
        skill, ok = QInputDialog.getItem(self, "Add Highlighted Skill", "Choose skill:", agg_skills, editable=False)
        if ok and skill:
            self.add_highlight_skill_row(skill)

    def remove_highlight_skill(self, row, skill_name):
        container = row.parentWidget()
        if container:
            self.highlight_skills_container.removeWidget(container)
            container.setParent(None)

    # ---------------- Save Changes ----------------
    def save_changes(self):
        if not self.current_project_name:
            return
        fa = self.manager.get_project_info(self.current_project_name)
        if not fa:
            return
        
        # Before updating attributes
        old_name = self.current_project_name
        new_name = self.name_edit.text()

        if old_name != new_name:
            self.manager.rename_project(old_name, new_name)
            self.current_project_name = new_name

        # Update attributes directly
        fa.file_name = self.name_edit.text()
        fa.created_time = self.created_time_edit.text()
        fa.last_modified = self.last_modified_edit.text()
        # fa.importance = str(self.importance_edit.value())
        fa.customized = str(self.customized_checkbox.isChecked())
        self.manager.set_project_rank(self.current_project_name, self.rank_spinbox.value())
        self.manager.set_showcase_flag(self.current_project_name, self.showcase_checkbox.isChecked())



        # Aggregate skills
        agg_skills = [self.agg_skills_container.itemAt(i).widget().layout().itemAt(0).widget().text()
                      for i in range(self.agg_skills_container.count())]
        self.manager.set_project_skills(self.current_project_name, ", ".join(agg_skills))

        # Highlighted skills
        highlight_skills = [self.highlight_skills_container.itemAt(i).widget().layout().itemAt(0).widget().text()
                            for i in range(self.highlight_skills_container.count())]
        self.manager.set_highlighted_skills(self.current_project_name, highlight_skills)

        self.refresh_project_list()

    # ---------------- Generate PDF ----------------
    def generate_resume(self):
        pdf_path = self.manager.get_full_resume_pdf()
        if not pdf_path:
            QMessageBox.warning(self, "Error", "Failed to generate resume PDF.")
            return
        msg = QMessageBox(self)
        msg.setWindowTitle("Resume Generated")
        msg.setText("Resume PDF generated successfully!")
        msg.setInformativeText(str(pdf_path))
        open_btn = msg.addButton("Open Folder", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Ok)
        msg.exec_()
        if msg.clickedButton() == open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path.parent)))

    def generate_portfolio(self):
        portfolio_path = self.manager.get_full_portfolio()
        if not portfolio_path:
            QMessageBox.warning(self, "Error", "Failed to generate portfolio.")
            return
        msg = QMessageBox(self)
        msg.setWindowTitle("Portfolio Generated")
        msg.setText("Portfolio ZIP generated successfully!")
        msg.setInformativeText(str(portfolio_path))
        open_btn = msg.addButton("Open Folder", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Ok)
        msg.exec_()
        if msg.clickedButton() == open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(portfolio_path.parent)))

    def open_skills_page(self):
        self.skills_page = SkillsPage(self.manager)
        self.skills_page.show()

    def refresh_from_scan(self):
        # Re-load log
        self.manager.load_log()
        self.refresh_project_list()
        
        # Optionally reload currently selected project
        if self.current_project_name:
            self.load_project(self.current_project_name)
