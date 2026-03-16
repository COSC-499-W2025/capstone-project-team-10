from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QStackedWidget, QDialog,
                             QDialogButtonBox, QMessageBox,
                             QFileDialog, QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon
import csv
from pathlib import Path
from src.fas.fas import FileAnalysis
import src.log.log as log
import utils.project_thumbnails as pt
import src.gui.gui_dashboard.gui_favourites_helper as fav_store
from src.gui.gui_dashboard.gui_project_files_page import ProjectFilesPage

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
        self.id_edit.setPlaceholderText("Enter Project ID")
        self.id_edit.setStyleSheet("color: black; padding: 6px; border: 1px solid #ccc; border-radius: 4px;")

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Optional description")
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

# Lists all project ids in selected log
class LogDetailsPage(QWidget):
    # Return to previous page
    back_clicked = pyqtSignal()
    project_created = pyqtSignal(str, str)

    favourites_changed = pyqtSignal()

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
        # Columns: thumbnail | project id | favourite button
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["", "Project ID", ""])

        # Thumbnail column: fixed width
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, thumbnail_size)

        # Project ID column: stretch
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Favourite button column: fixed width
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 130)

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
            QScrollBar:vertical {
                margin-right: 4px;
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
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

        self.stack.addWidget(self.projects_widget)

        self.project_files_page = ProjectFilesPage()

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

                self.table.setItem(idx, 1, QTableWidgetItem(pid))

                self._insert_fav_button(idx, pid)

        except Exception as e:
            print(f"Error loading CSV: {e}")

        self.thumbnail_btn.setEnabled(False)

    def _fav_button_style(self, is_fav: bool) -> str:
        if is_fav:
            return """
                QPushButton {
                    background-color: #002145;
                    color: white;
                    border: none;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #003366; }
            """
        return """
            QPushButton {
                background-color: #e0e0e0;
                color: #444;
                border: none;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #c8c8c8; }
        """

    def _insert_fav_button(self, row: int, project_id: str):
        # Create the favourite toggle button for a table row.
        is_fav = fav_store.is_favourite(project_id, self.log_path)
        btn = QPushButton("Favourited" if is_fav else "Favourite")
        btn.setStyleSheet(self._fav_button_style(is_fav))
        btn.setToolTip(
            "Remove from favourites" if is_fav else "Add to favourites"
        )
        btn.clicked.connect(
            lambda checked, pid=project_id, b=btn: self._on_toggle_favourite(pid, b)
        )
        self.table.setCellWidget(row, 2, btn)

    def _on_toggle_favourite(self, project_id: str, btn: QPushButton):
        # Toggle the favourite state and update the button appearance.
        now_fav = fav_store.toggle_favourite(project_id, self.log_path)
        btn.setText("Favourited" if now_fav else "Favourite")
        btn.setStyleSheet(self._fav_button_style(now_fav))
        btn.setToolTip("Remove from favourites" if now_fav else "Add to favourites")
        self.favourites_changed.emit()

    def on_selection_changed(self):
        # Enable the thumbnail button only when a project row is selected.
        has_selection = bool(self.table.selectedItems())
        self.thumbnail_btn.setEnabled(has_selection)

    def on_select_thumbnail(self):
        # Open file dialog to pick a thumbnail for the selected project.
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
                file_hash="",
            )
            log.current_projects.add(new_id)
            log.write(project_fa)
        except Exception as e:
            styled_msgbox(self, "Error", f"Could not save project to log: {e}", QMessageBox.Warning).exec_()
            return

        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, thumbnail_size)

        thumb_item = QTableWidgetItem()
        thumb_item.setIcon(QIcon(empty_thumbnail(thumbnail_size)))
        self.table.setItem(row_idx, 0, thumb_item)
        self.table.setItem(row_idx, 1, QTableWidgetItem(new_id))
        self._insert_fav_button(row_idx, new_id)

        self._project_ids.append(new_id)
        self.project_created.emit(new_id, description)

        styled_msgbox(self, "Project Created", f"Project '<b>{new_id}</b>' has been created.").exec_()

    # Double click to enter next page
    def on_double_clicked(self, row, _col):
        project_id = self.table.item(row, 1).text()
        files = log.get_project(project_id)
        self.project_files_page.load_project_files(project_id, files)
        self.stack.setCurrentIndex(1)