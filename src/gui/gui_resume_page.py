from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QFileDialog,
    QMessageBox, QSpinBox, QScrollArea, QInputDialog, QDateEdit, QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt, QUrl, QDate
from PyQt5.QtGui import QDesktopServices
from pathlib import Path

from src.gui.gui_skills_page import SkillsPage
from src.gui.gui_resume_manager import ResumeManager


class ResumePage(QWidget):
    """
    Resume editor page.
    - Uses QDateEdit for start/end date (calendar popup)
    - No file_type
    - No customized checkbox
    - Uses project_description
    """

    def __init__(self):
        super().__init__()
        self.manager = ResumeManager()
        self.current_project_id = None
        # Local include-in-showcase flags (session-only)
        # self.session_include_flags = {} 

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # ---------------- LEFT PANEL ----------------
        left_panel = QVBoxLayout()

        # Log chooser
        log_row = QHBoxLayout()
        self.log_label = QLabel("Current log:")
        self.log_path_label = QLabel(str(self.manager.log_file))
        self.log_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.choose_log_btn = QPushButton("Choose Log...")
        self.choose_log_btn.clicked.connect(self.choose_log_file)

        log_row.addWidget(self.log_label)
        log_row.addWidget(self.choose_log_btn)

        left_panel.addLayout(log_row)
        left_panel.addWidget(self.log_path_label)

        # Project list
        self.project_list = QListWidget()
        self.project_list.setDragDropMode(QListWidget.InternalMove)
        self.project_list.currentItemChanged.connect(self.load_project)

        left_panel.addWidget(QLabel("Projects:"))
        left_panel.addWidget(self.project_list)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        layout.addWidget(left_widget, 1)

        # ---------------- RIGHT PANEL ----------------
        editor_layout = QVBoxLayout()

        # Project Name
        editor_layout.addWidget(QLabel("Project Name:"))
        self.name_edit = QLineEdit()
        editor_layout.addWidget(self.name_edit)

        # Start / End Dates using QDateEdit
        editor_layout.addWidget(QLabel("Start Date:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        editor_layout.addWidget(self.start_date_edit)

        editor_layout.addWidget(QLabel("End Date:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        editor_layout.addWidget(self.end_date_edit)

        # # Last Modified
        # editor_layout.addWidget(QLabel("Last Modified:"))
        # self.last_modified_edit = QLineEdit()
        # editor_layout.addWidget(self.last_modified_edit)

        # Project Rank & Showcase
        editor_layout.addWidget(QLabel("Project Rank:"))
        self.rank_spinbox = QSpinBox()
        self.rank_spinbox.setRange(0, 1000)
        editor_layout.addWidget(self.rank_spinbox)

        self.showcase_checkbox = QCheckBox("Include in Showcase")
        editor_layout.addWidget(self.showcase_checkbox)
        # self.showcase_checkbox.stateChanged.connect(
        #     lambda state: self.update_include_flag(self.current_project_id, state)
        # )

        # Project Description
        editor_layout.addWidget(QLabel("Project Description:"))
        # self.description_edit = QTextEdit()
        self.description_edit = QLineEdit()
        editor_layout.addWidget(self.description_edit)

        # ---------------- AGGREGATED SKILLS ----------------
        editor_layout.addWidget(QLabel("Skills (all files):"))
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

        # ---------------- BUTTONS ----------------
        btn_layout = QHBoxLayout()
        self.skills_page_btn = QPushButton("View Skills")
        self.skills_page_btn.clicked.connect(self.open_skills_page)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)

        self.generate_resume_btn = QPushButton("Generate Resume PDF")
        self.generate_resume_btn.clicked.connect(self.generate_resume)

        self.generate_portfolio_btn = QPushButton("Generate Portfolio")
        self.generate_portfolio_btn.clicked.connect(self.generate_portfolio)

        btn_layout.addWidget(self.skills_page_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.generate_resume_btn)
        btn_layout.addWidget(self.generate_portfolio_btn)

        editor_layout.addLayout(btn_layout)

        editor_widget = QWidget()
        editor_widget.setLayout(editor_layout)
        layout.addWidget(editor_widget, 3)

        self.refresh_project_list()

    # ---------------- LOG ----------------
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

        self.current_project_id = None
        self.clear_editor()
        self.project_list.clear()

        self.manager = ResumeManager(log_file=chosen)
        self.log_path_label.setText(str(self.manager.log_file))
        self.refresh_project_list()

    # ---------------- PROJECT LIST ----------------
    def refresh_project_list(self):
        self.project_list.blockSignals(True)
        self.project_list.clear()

        # # Reset local session include flags
        # self.session_include_flags = {
        #     proj.project_id: True for proj in self.manager.projects.values()
        # }

        projects_sorted = sorted(
            self.manager.projects.values(),
            key=lambda x: self.manager.get_project_extra_attributes(
                x.project_id
            ).get("project_rank", 0)
        )

        for proj in projects_sorted:
            item = QListWidgetItem(proj.file_name)
            item.setData(Qt.UserRole, proj.project_id)
            self.project_list.addItem(item)

        self.project_list.blockSignals(False)
        self.current_project_id = None

    # ---------------- EDITOR ----------------
    def clear_editor(self):
        self.name_edit.clear()
        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDate(QDate.currentDate())
        # self.last_modified_edit.clear()
        self.rank_spinbox.setValue(0)
        self.showcase_checkbox.setChecked(False)
        self.description_edit.clear()
        self.clear_skill_lists()

    def load_project(self, current, previous=None):
        if not current:
            return

        project_id = current.data(Qt.UserRole)
        self.current_project_id = project_id
        fa = self.manager.get_project_info(project_id)
        if not fa:
            return

        self.name_edit.setText(fa.file_name)

        extra = self.manager.get_project_extra_attributes(project_id)
        start_date = extra.get("start_date", QDate.currentDate().toString("yyyy-MM-dd"))
        end_date = extra.get("end_date", QDate.currentDate().toString("yyyy-MM-dd"))

        self.start_date_edit.setDate(QDate.fromString(start_date, "yyyy-MM-dd"))
        self.end_date_edit.setDate(QDate.fromString(end_date, "yyyy-MM-dd"))
        self.rank_spinbox.setValue(extra.get("project_rank", 0))

        # ---------------- USE SESSION FLAG ----------------
        # include_flag = self.session_include_flags.get(project_id, True)
        # self.showcase_checkbox.setChecked(include_flag)

        include_flag = extra.get("include", True)
        self.showcase_checkbox.setChecked(include_flag)

        self.description_edit.setText(extra.get("project_description", ""))

        # Load aggregated skills
        self.clear_skill_lists()
        agg_skills = self.manager.get_project_skills(project_id)
        for skill in agg_skills:
            self.add_aggregate_skill_row(skill)

    # ---------------- SKILLS ----------------
    def clear_skill_lists(self):
        for i in reversed(range(self.agg_skills_container.count())):
            widget = self.agg_skills_container.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def add_aggregate_skill_row(self, skill_name):
        row = QHBoxLayout()
        label = QLabel(skill_name)
        remove_btn = QPushButton("-")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_skill_row(row))
        row.addWidget(label)
        row.addWidget(remove_btn)

        container = QWidget()
        container.setLayout(row)
        self.agg_skills_container.addWidget(container)

    def add_aggregate_skill(self):
        text, ok = QInputDialog.getText(self, "Add Skill", "Skill Name:")
        if ok and text.strip():
            self.add_aggregate_skill_row(text.strip())

    def remove_skill_row(self, row):
        container = row.parentWidget()
        if container:
            self.agg_skills_container.removeWidget(container)
            container.setParent(None)

    # ---------------- SAVE ----------------
    # def save_changes(self):
    #     if not self.current_project_id:
    #         return

    #     fa = self.manager.get_project_info(self.current_project_id)
    #     if not fa:
    #         return

    #     # Rename display name only
    #     new_name = self.name_edit.text()
    #     if fa.file_name != new_name:
    #         self.manager.rename_project(self.current_project_id, new_name)

    #     fa.file_name = new_name
    #     # fa.last_modified = self.last_modified_edit.text()

    #     # Save extra fields
    #     self.manager.set_project_rank(self.current_project_id, self.rank_spinbox.value())
    #     self.manager.set_showcase_flag(self.current_project_id, self.showcase_checkbox.isChecked())
    #     self.manager.set_project_description(self.current_project_id, self.description_edit.text())

    #     self.manager.set_project_dates(
    #         self.current_project_id,
    #         start_date=self.start_date_edit.date().toString("yyyy-MM-dd"),
    #         end_date=self.end_date_edit.date().toString("yyyy-MM-dd")
    #     )

    #     # Aggregate skills
    #     agg_skills = [
    #         self.agg_skills_container.itemAt(i).widget().layout().itemAt(0).widget().text()
    #         for i in range(self.agg_skills_container.count())
    #     ]
    #     self.manager.set_project_skills(self.current_project_id, ", ".join(agg_skills))

    #     self.refresh_project_list()
    def save_changes(self):
        if not self.current_project_id:
            return

        fa = self.manager.get_project_info(self.current_project_id)
        if not fa:
            return

        # Update project name if changed
        new_name = self.name_edit.text()
        if fa.file_name != new_name:
            self.manager.rename_project(self.current_project_id, new_name)
            fa.file_name = new_name

        # Update extra fields
        self.manager.set_project_rank(self.current_project_id, self.rank_spinbox.value())
        self.manager.set_showcase_flag(self.current_project_id, self.showcase_checkbox.isChecked())
        self.manager.set_project_description(self.current_project_id, self.description_edit.text())

        # Update start/end dates
        self.manager.set_project_dates(
            self.current_project_id,
            start_date=self.start_date_edit.date().toString("yyyy-MM-dd"),
            end_date=self.end_date_edit.date().toString("yyyy-MM-dd")
        )

        # Aggregate skills
        agg_skills = [
            self.agg_skills_container.itemAt(i).widget().layout().itemAt(0).widget().text()
            for i in range(self.agg_skills_container.count())
        ]
        self.manager.set_project_skills(self.current_project_id, ", ".join(agg_skills))

        # Refresh left sidebar list and keep selection
        self.refresh_project_list()
        items = self.project_list.findItems(fa.file_name, Qt.MatchExactly)
        if items:
            self.project_list.setCurrentItem(items[0])

        # Show confirmation alert
        QMessageBox.information(self, "Saved", f"Project '{fa.file_name}' saved successfully!")

    # ---------------- GENERATION ----------------

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
            QMessageBox.warning(self, "Error", "Failed to generate portfolio ZIP.")
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

    # ---------------- OTHER ----------------
    def open_skills_page(self):
        self.skills_page = SkillsPage(self.manager)
        self.skills_page.show()

    def refresh_from_scan(self):
        self.manager.load_log()
        self.refresh_project_list()

    # def update_include_flag(self, project_id, state):
    #     if project_id:
    #         self.session_include_flags[project_id] = bool(state)