from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QStackedWidget, QDialog,
                             QDialogButtonBox, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal
import csv
from pathlib import Path
from src.fas.fas import FileAnalysis
import src.log.log as log

# Shows all files not currently in project but in the same log
class AddFileDialog(QDialog):

    def __init__(self, current_project_id: str, log_path: Path, parent=None):
        super().__init__(parent)
        self.current_project_id = current_project_id
        self.log_path = log_path
        self.selected_files = []
        self.setWindowTitle("Add Files from Other Projects")
        self.resize(700, 450)
        self._init_ui()
        self.load_other_projects()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Info label
        info = QLabel(f"Select files to move into project <b>{self.current_project_id}</b>.")
        info.setStyleSheet("color: black; font-size: 13px;")
        layout.addWidget(info)

        # Table for files from other projects
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["File Name", "File Type", "Created Time", "Importance", "Source Project"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { 
                background-color: white; 
                color: black; 
                gridline-color: #e0e0e0; 
                border: none; 
            }
            QHeaderView::section { 
                background-color: white; 
                padding: 8px; 
                border-bottom: 1px solid #e0e0e0; 
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
        layout.addWidget(self.table)

        # Accept / Cancel buttons
        btn_style = """
            QPushButton {
                background-color: #002145;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #003366; }
        """

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Add Selected")
        buttons.button(QDialogButtonBox.Ok).setStyleSheet(btn_style)
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet(btn_style)
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # Load in all other files not currently in the project
    def load_other_projects(self):
        self._rows = []
        if not self.log_path or not self.log_path.exists():
            return

        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pid = row.get("Project id", "").strip()
                    if pid != self.current_project_id:
                        self._rows.append(row)
        except Exception as e:
            print(f"Error loading files for dialog: {e}")

        for idx, row in enumerate(self._rows):
            self.table.insertRow(idx)
            self.table.setItem(idx, 0, QTableWidgetItem(row.get("File name", "")))
            self.table.setItem(idx, 1, QTableWidgetItem(row.get("File type", "")))
            self.table.setItem(idx, 2, QTableWidgetItem(row.get("Created time", "")))
            self.table.setItem(idx, 3, QTableWidgetItem(row.get("Importance", "")))
            self.table.setItem(idx, 4, QTableWidgetItem(row.get("Project id", "")))

    def on_accept(self):
        selected_rows = set(idx.row() for idx in self.table.selectedIndexes())
        self.selected_files = [self._rows[r] for r in selected_rows]
        self.accept()

# Page for individual projects
class ProjectFilesPage(QWidget):
    # Return to previous page
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_project_id = None
        self._log_path = None
        self.setStyleSheet("background-color: white;")
        self._init_ui()

    def set_log_path(self, log_path: Path):
        self._log_path = log_path

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        # Back Button
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
            QPushButton:hover { background-color: #003366; }
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)

        # Project title
        self.title_label = QLabel("Project Files")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        btn_style = """
            QPushButton {
                background-color: #002145;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #003366; }
            QPushButton:disabled { background-color: #aaa; }
        """

        # Add file button
        self.add_btn = QPushButton("＋ Add File")
        self.add_btn.setStyleSheet(btn_style)
        self.add_btn.clicked.connect(self.on_file_add)
        header_layout.addWidget(self.add_btn)

        # Remove file button
        self.remove_btn = QPushButton("✕ Remove File")
        self.remove_btn.setStyleSheet(btn_style)
        self.remove_btn.setEnabled(False)   # Enabled only when a row is selected
        self.remove_btn.clicked.connect(self.on_file_remove)
        header_layout.addWidget(self.remove_btn)

        layout.addLayout(header_layout)

        # File table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File Name", "File Type", "Created Time", "Importance"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 4):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
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
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)

    # Load files into table for given project
    def load_project_files(self, project_id: str, files):
        self._current_project_id = project_id
        self.title_label.setText(f"Files in Project: {project_id}")
        self.table.setRowCount(0)

        for idx, fa in enumerate(files):
            self.table.insertRow(idx)
        
            name_item = QTableWidgetItem(str(fa.file_name))
        
            name_item.setData(Qt.UserRole, fa) 
        
            self.table.setItem(idx, 0, name_item)
            self.table.setItem(idx, 1, QTableWidgetItem(str(fa.file_type)))
            self.table.setItem(idx, 2, QTableWidgetItem(str(fa.created_time)))
            self.table.setItem(idx, 3, QTableWidgetItem(str(fa.importance)))

        self.remove_btn.setEnabled(False)

    def on_selection_changed(self):
        has_selection = bool(self.table.selectedItems())
        self.remove_btn.setEnabled(has_selection)

    # Remove selected file from given project
    def on_file_remove(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        rows_to_remove = sorted([index.row() for index in selected_rows], reverse=True)

        # Confirmation box for user
        btn_style = """
            QPushButton {
                background-color: #002145;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #003366; }
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Remove File")
        msg.setText(f"Remove {len(selected_rows)} file from project '{self._current_project_id}'?")
        msg.setStyleSheet("QLabel { color: black; font-weight: normal; }")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        for button in msg.buttons():
            button.setStyleSheet(btn_style)
        confirm = msg.exec_()
        if confirm != QMessageBox.Yes:
            return

        # Removes file by setting its project_id to blank via log.update()
        for row in rows_to_remove:
            fa = self.table.item(row, 0).data(Qt.UserRole)
        
            if fa:
                try:
                    fa.project_id = "" 
                    log.update(fa, forceUpdate=True)
                    self.table.removeRow(row)
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Could not remove '{fa.file_name}': {e}")

    # Add selected file to a given project
    def on_file_add(self):
        if not self._current_project_id:
            return

        dlg = AddFileDialog(self._current_project_id, self._log_path, parent=self)
        if dlg.exec_() != QDialog.Accepted:
            return

        for row_dict in dlg.selected_files:
            fa = FileAnalysis(
                file_path=row_dict.get("File path analyzed", "").strip(),
                file_name=row_dict.get("File name", "").strip(),
                file_type=row_dict.get("File type", "").strip(),
                last_modified=row_dict.get("Last modified", "").strip(),
                created_time=row_dict.get("Created time", "").strip(),
                extra_data=row_dict.get("Extra data", "").strip(),
                importance=row_dict.get("Importance", "").strip(),
                customized=row_dict.get("Customized", "False").strip(),
                project_id=self._current_project_id,
                file_hash=row_dict.get("File hash", "").strip(),
            )
            try:
                log.update(fa, forceUpdate=True)

                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)

                name_item = QTableWidgetItem(fa.file_name)
                name_item.setData(Qt.UserRole, fa)

                self.table.setItem(row_idx, 0, name_item)
                self.table.setItem(row_idx, 1, QTableWidgetItem(fa.file_type))
                self.table.setItem(row_idx, 2, QTableWidgetItem(fa.created_time))
                self.table.setItem(row_idx, 3, QTableWidgetItem(fa.importance))

            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Could not add file: {e}")

# Lists all project ids in selected log
class LogDetailsPage(QWidget):
    # Return to previous page
    back_clicked = pyqtSignal()

    def __init__(self, log_path=None, parent=None):
        super().__init__(parent)
        self.log_path = log_path
        self._project_ids = []
        self.setStyleSheet("background-color: white;")
        self._init_ui()
        if log_path:
            self.load_log_files()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)
        
        # Project list
        self.projects_widget = QWidget()
        layout = QVBoxLayout(self.projects_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton{
                background-color: #002145; 
                color: white; 
                padding: 8px; 
                border-radius: 4px;}
            QPushButton:hover { 
                background-color: #003366; 
            }""")
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)

        self.title_label = QLabel("Log Details")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Table containing project ids
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
                color: white; }
        """)
        self.table.cellDoubleClicked.connect(self.on_double_clicked)
        layout.addWidget(self.table)
        self.stack.addWidget(self.projects_widget)

        self.project_files_page = ProjectFilesPage()

        self.project_files_page.back_clicked.connect(
            lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.project_files_page)

    def set_log_path(self, log_path: Path):
        self.log_path = log_path
        self.project_files_page.set_log_path(log_path)
        if hasattr(log_path, 'name'):
            self.title_label.setText(f"Projects in: {log_path.name}")
        self.load_log_files()

    # Populate project ids table from log
    def load_log_files(self):
        self.table.setRowCount(0)
        self._project_ids = []
        projects = set()

        self.project_files_page.set_log_path(self.log_path)

        if not self.log_path or not self.log_path.exists():
            return

        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pid = row.get("Project id", "").strip()
                    if pid and pid not in projects:
                        projects.add(pid)
                        self._project_ids.append(pid)

            for idx, pid in enumerate(self._project_ids):
                self.table.insertRow(idx)
                self.table.setItem(idx, 0, QTableWidgetItem(pid))

        except Exception as e:
            print(f"Error loading CSV: {e}")

    # Double click to enter next page
    def on_double_clicked(self, row, _col):
        project_id = self.table.item(row, 0).text()
        files = log.get_project(project_id)
        self.project_files_page.load_project_files(project_id, files)
        self.stack.setCurrentIndex(1)