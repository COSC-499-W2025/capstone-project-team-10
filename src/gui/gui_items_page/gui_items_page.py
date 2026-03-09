from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
import subprocess
from pathlib import Path
from datetime import datetime
from .gui_items_manager import GuiItemsManager


class ItemsPage(QWidget):
    """GUI page for viewing generated items."""

    def __init__(self):
        super().__init__()
        self.manager = GuiItemsManager()
        self.current_items = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Backup", "Original", "Creation Date", "Type", "Source Log"]
        )
        self.table.verticalHeader().setVisible(False)  # remove numbering on far left
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Remove dashed focus rectangle on cells
        self.table.setFocusPolicy(Qt.NoFocus)

        # Header border + clean cell focus/selection visuals
        self.table.setStyleSheet(
            """
            QHeaderView::section {
                border: 1px solid #bfbfbf;
                border-left: none;
                border-top: none;
                padding: 6px;
                font-weight: bold;
                background: #f5f5f5;
            }
            QHeaderView::section:first {
                border-left: 1px solid #bfbfbf;
            }
            QTableWidget::item:focus {
                outline: none;
            }
            """
        )

        # Bold headers
        header_font = self.table.horizontalHeader().font()
        header_font.setBold(True)
        self.table.horizontalHeader().setFont(header_font)

        layout.addWidget(self.table, 1)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.visit_btn = QPushButton("Visit File")
        self.visit_btn.clicked.connect(self.visit_selected_file)

        button_layout.addStretch()
        button_layout.addWidget(self.visit_btn)

        layout.addLayout(button_layout)

    def _format_type(self, raw_type: str) -> str:
        if raw_type == "pdf_resume":
            return "Resume"
        if raw_type == "web_portfolio":
            return "Portfolio"
        return raw_type.replace("_", " ").title() if raw_type else ""

    def _format_datetime(self, raw_datetime: str) -> str:
        if not raw_datetime:
            return ""
        try:
            dt = datetime.fromisoformat(raw_datetime)
            return dt.strftime("%b %d, %Y %I:%M %p")
        except ValueError:
            return raw_datetime

    def showEvent(self, event):
        super().showEvent(event)
        self.load_and_validate_items()

    def load_and_validate_items(self):
        items = self.manager.load_items()
        removed_items = []

        valid_items = []
        for item in items:
            file_path = item.get("path", "")
            if file_path and Path(file_path).exists():
                valid_items.append(item)
            else:
                removed_items.append(item)

        if removed_items:
            self.manager.save_items(valid_items)
            self.show_removed_items_popup(removed_items)

        self.load_items_table(valid_items)

    def load_items_table(self, items):
        self.current_items = items
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            id_item = QTableWidgetItem(str(item.get("id", "")))
            id_item.setTextAlignment(Qt.AlignCenter)

            backup_item = QTableWidgetItem(item.get("file_name", ""))
            original_item = QTableWidgetItem(item.get("original", ""))
            created_item = QTableWidgetItem(self._format_datetime(item.get("created_at", "")))

            type_item = QTableWidgetItem(self._format_type(item.get("type", "")))
            type_item.setTextAlignment(Qt.AlignCenter)

            source_item = QTableWidgetItem(item.get("source_log", ""))

            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, backup_item)
            self.table.setItem(row, 2, original_item)
            self.table.setItem(row, 3, created_item)
            self.table.setItem(row, 4, type_item)
            self.table.setItem(row, 5, source_item)

        self.resize_columns()

    def resize_columns(self):
        self.table.setColumnWidth(0, int(self.table.width() * 0.08))  # ID
        self.table.setColumnWidth(1, int(self.table.width() * 0.15))  # Backup
        self.table.setColumnWidth(2, int(self.table.width() * 0.17))  # Original
        self.table.setColumnWidth(3, int(self.table.width() * 0.20))  # Creation Date
        self.table.setColumnWidth(4, int(self.table.width() * 0.12))  # Type
        self.table.setColumnWidth(5, int(self.table.width() * 0.28))  # Source Log

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_columns()

    def visit_selected_file(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to visit.")
            return

        if current_row >= len(self.current_items):
            QMessageBox.warning(self, "Invalid Selection", "Selected row is invalid.")
            return

        location = self.current_items[current_row].get("path", "")
        if not location:
            QMessageBox.warning(self, "Invalid Path", "File path is empty.")
            return

        file_path = Path(location)
        if not file_path.exists():
            QMessageBox.critical(self, "File Not Found", f"File not found:\n{location}")
            return

        try:
            subprocess.Popen(f'explorer /select,"{file_path}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file location:\n{str(e)}")

    def show_removed_items_popup(self, removed_items):
        removed_names = [item.get("original", "Unknown") for item in removed_items]
        message = "The following items were removed because their files no longer exist:\n\n" + "\n".join(removed_names)
        QMessageBox.information(self, "Invalidated Items", message)