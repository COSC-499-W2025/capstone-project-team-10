from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialogButtonBox,
                             QAbstractItemView)
from PyQt5.QtCore import Qt
import csv
from pathlib import Path


class AddFileDialog(QDialog):
    """Shows all files not currently in the project but in the same log."""

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

        info = QLabel(f"Select files to move into project <b>{self.current_project_id}</b>.")
        info.setStyleSheet("color: black; font-size: 13px;")
        layout.addWidget(info)

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