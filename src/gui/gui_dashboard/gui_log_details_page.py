from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QStackedWidget, QDialog,
                             QDialogButtonBox, QMessageBox, QAbstractItemView,
                             QFileDialog, QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon
import csv
from pathlib import Path
from src.fas.fas import FileAnalysis
import src.log.log as log
import utils.project_thumbnails as pt

thumbnail_size = 128

def empty_thumbnail(size: int = thumbnail_size) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    return pixmap

def create_thumbnail(image_path: str, size: int = thumbnail_size) -> QPixmap:
    """
    Load an image from disk and scale it to a fixed size.
    Returns the placeholder if the path is invalid.
    """
    if not image_path or not Path(image_path).is_file():
        return empty_thumbnail(size)

    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        return empty_thumbnail(size)

    return pixmap.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

def styled_msgbox(parent, title: str, text: str, icon=QMessageBox.Information) -> QMessageBox:
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    msg.setStyleSheet("""
        QLabel { color: black; font-weight: normal; }
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
    return msg

class CreateProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.resize(420, 200)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("e.g. my-project-2024")
        self.id_edit.setStyleSheet("color: black; padding: 6px; border: 1px solid #ccc; border-radius: 4px;")

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Optional short description")
        self.desc_edit.setStyleSheet("color: black; padding: 6px; border: 1px solid #ccc; border-radius: 4px;")

        lbl_style = "color: black; font-size: 13px;"
        id_lbl = QLabel("Project ID:")
        id_lbl.setStyleSheet(lbl_style)
        desc_lbl = QLabel("Description:")
        desc_lbl.setStyleSheet(lbl_style)

        form.addRow(id_lbl, self.id_edit)
        form.addRow(desc_lbl, self.desc_edit)
        layout.addLayout(form)

        BUTTON_STYLE = """
            QPushButton {
                background-color: #002145;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #003366; }
            QPushButton:disabled { background-color: #aaa; }
        """

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Create Project")
        buttons.button(QDialogButtonBox.Ok).setStyleSheet(BUTTON_STYLE)
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet(BUTTON_STYLE)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        if not self.id_edit.text().strip():
            QMessageBox.warning(self, "Missing Field", "Project ID cannot be empty.")
            return
        self.accept()

    def project_id(self) -> str:
        return self.id_edit.text().strip()

    def description(self) -> str:
        return self.desc_edit.text().strip()

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
                    styled_msgbox(self, "Warning", f"Could not remove '{fa.file_name}': {e}", QMessageBox.Warning).exec_()

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
    project_created = pyqtSignal(str, str)

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

        # Table containing project ids with thumbnail column
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["", "Project ID"])

        # Thumbnail column: fixed width
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, thumbnail_size)

        # Project ID column: stretch
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setIconSize(QSize(thumbnail_size, thumbnail_size))
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
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.thumbnail_btn = QPushButton("Select Thumbnail")
        self.thumbnail_btn.setStyleSheet("""color: black;""")
        self.thumbnail_btn.setEnabled(False)
        self.thumbnail_btn.clicked.connect(self.on_select_thumbnail)
        bottom_layout.addWidget(self.thumbnail_btn)

        self.new_project_btn = QPushButton("New Project")
        self.new_project_btn.setStyleSheet("""color: black;""")
        self.new_project_btn.setToolTip("Create a new custom project in this log")
        self.new_project_btn.clicked.connect(self.on_new_project)
        bottom_layout.addWidget(self.new_project_btn)

        layout.addLayout(bottom_layout)

        layout.addLayout(bottom_layout)
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
                self.table.setRowHeight(idx, thumbnail_size)

                thumb_path = pt.get_thumbnail(pid)
                pixmap = create_thumbnail(thumb_path, thumbnail_size)
                thumb_item = QTableWidgetItem()
                thumb_item.setIcon(QIcon(pixmap))
                self.table.setItem(idx, 0, thumb_item)

                # Project ID cell
                self.table.setItem(idx, 1, QTableWidgetItem(pid))

        except Exception as e:
            print(f"Error loading CSV: {e}")

        self.thumbnail_btn.setEnabled(False)

    def on_selection_changed(self):
        """Enable the thumbnail button only when a project row is selected."""
        has_selection = bool(self.table.selectedItems())
        self.thumbnail_btn.setEnabled(has_selection)

    def on_select_thumbnail(self):
        """Open file dialog to pick a thumbnail for the selected project."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        project_id = self.table.item(row, 1).text()

        image_filter = "Images (*.png *.jpg *.jpeg *.bmp *.gif *.svg *.webp);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select Thumbnail for '{project_id}'",
            "",
            image_filter
        )

        if not file_path:
            return

        if not Path(file_path).is_file():
            QMessageBox.warning(self, "Invalid File", "The selected file does not exist.")
            return

        success = pt.set_thumbnail(project_id, file_path)
        if not success:
            QMessageBox.warning(self, "Error", "Could not save thumbnail. File may not exist.")
            return

        # Update the table cell immediately
        pixmap = create_thumbnail(file_path, thumbnail_size)
        self.table.item(row, 0).setIcon(QIcon(pixmap))

    def on_new_project(self):
        dlg = CreateProjectDialog(parent=self)
        if dlg.exec_() != QDialog.Accepted:
            return

        new_id = dlg.project_id()
        description = dlg.description()

        if new_id in self._project_ids:
            styled_msgbox(self, "Duplicate ID", f"A project with ID '{new_id}' already exists in this log.", QMessageBox.Warning).exec_()
            return

        # Write the new project entry to the log
        try:
            project_fa = FileAnalysis(
                file_path=new_id,
                file_name=new_id,
                file_type="Project",
                last_modified="",
                created_time="",
                extra_data={"description": description},
                importance=0.0,
                customized=True,
                project_id=new_id,
                file_hash= "", # Set to be empty in accordance with the other projects
            )
            log.current_projects.add(new_id)
            log.write(project_fa)
        except Exception as e:
            styled_msgbox(self, "Error", f"Could not save project to log: {e}", QMessageBox.Warning).exec_()
            return

        # Insert into the table
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, thumbnail_size)

        thumb_item = QTableWidgetItem()
        thumb_item.setIcon(QIcon(empty_thumbnail(thumbnail_size)))
        self.table.setItem(row_idx, 0, thumb_item)
        self.table.setItem(row_idx, 1, QTableWidgetItem(new_id))

        self._project_ids.append(new_id)
        self.project_created.emit(new_id, description)

        styled_msgbox(self, "Project Created", f"Project '<b>{new_id}</b>' has been created.").exec_()

    # Double click to enter next page
    def on_double_clicked(self, row, _col):
        project_id = self.table.item(row, 1).text()
        files = log.get_project(project_id)
        self.project_files_page.load_project_files(project_id, files)
        self.stack.setCurrentIndex(1)