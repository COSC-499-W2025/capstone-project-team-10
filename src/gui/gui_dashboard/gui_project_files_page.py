from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from pathlib import Path
from src.fas.fas import FileAnalysis
import src.log.log as log
import src.gui.gui_utils.gui_styles as styles
from src.gui.gui_dashboard.gui_add_file_dialouge import AddFileDialog


def styled_msgbox(parent, title: str, text: str, icon=QMessageBox.Information) -> QMessageBox:
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    msg.setStyleSheet("QLabel { color: black; font-weight: normal; }")
    for button in msg.buttons():
        button.setStyleSheet(styles.BUTTON_STYLE)
    return msg


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
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(styles.BUTTON_STYLE)
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)

        # Project title
        self.title_label = QLabel("Project Files")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Add file button
        self.add_btn = QPushButton("＋ Add File")
        self.add_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.add_btn.clicked.connect(self.on_file_add)
        header_layout.addWidget(self.add_btn)

        # Remove file button
        self.remove_btn = QPushButton("✕ Remove File")
        self.remove_btn.setStyleSheet(styles.BUTTON_STYLE)
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

        msg = QMessageBox(self)
        msg.setWindowTitle("Remove File")
        msg.setText(f"Remove {len(selected_rows)} file from project '{self._current_project_id}'?")
        msg.setStyleSheet("QLabel { color: black; font-weight: normal; }")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        for button in msg.buttons():
            button.setStyleSheet(styles.BUTTON_STYLE)
        confirm = msg.exec_()
        if confirm != QMessageBox.Yes:
            return

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