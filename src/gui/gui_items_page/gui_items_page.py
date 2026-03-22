from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from datetime import datetime
import subprocess
from pathlib import Path
from .gui_items_manager import GuiItemsManager


class ItemsPage(QWidget):
    """GUI page for viewing generated items."""

    def __init__(self):
        super().__init__()
        self.manager = GuiItemsManager()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Location", "Created", "Log File"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table, 1)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.visit_file_btn = QPushButton("Visit File")
        self.visit_file_btn.clicked.connect(self.visit_selected_file)

        self.visit_log_btn = QPushButton("Visit Log File")
        self.visit_log_btn.clicked.connect(self.visit_selected_log_file)

        self.visit_backup_btn = QPushButton("Visit Backup File")
        self.visit_backup_btn.clicked.connect(self.visit_selected_backup_file)

        button_layout.addStretch()
        button_layout.addWidget(self.visit_file_btn)
        button_layout.addWidget(self.visit_log_btn)
        button_layout.addWidget(self.visit_backup_btn)

        layout.addLayout(button_layout)

    def showEvent(self, event):
        """Load and validate items when page is shown"""
        super().showEvent(event)
        self.load_and_validate_items()

    def load_and_validate_items(self):
        """Load items, validate files exist, remove invalid entries, and show popup if items were removed"""
        items = self.manager.load_items()
        removed_items = []

        # Check which files no longer exist
        valid_items = []
        for item in items:
            original_path = item.get("path", "")
            backup_path = item.get("backup_path", "")
            original_exists = bool(original_path) and Path(original_path).exists()
            backup_exists = bool(backup_path) and Path(backup_path).exists()

            if original_exists or backup_exists:
                valid_items.append(item)
            else:
                removed_items.append(item)

        # If items were removed, update the JSON and show popup
        if removed_items:
            self.manager.save_items(valid_items)
            self.show_removed_items_popup(removed_items)

        # Load the validated items into the table
        self.load_items_table(valid_items)

    def load_items_table(self, items):
        """Load items from manager and populate table"""
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            name = item.get("name", "")
            file_type = self.clean_type(item.get("type", ""))
            original_location = item.get("path", "")
            backup_location = item.get("backup_path", "")
            created = self.format_datetime(item.get("created_at", ""))
            full_log_path = item.get("log", "")
            log_file = self.clean_log_file_name(full_log_path)

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(file_type))

            location_item = QTableWidgetItem(original_location)
            location_item.setData(Qt.UserRole, original_location)
            location_item.setData(Qt.UserRole + 1, backup_location)
            self.table.setItem(row, 2, location_item)

            self.table.setItem(row, 3, QTableWidgetItem(created))

            log_item = QTableWidgetItem(log_file)
            log_item.setData(Qt.UserRole, full_log_path)
            self.table.setItem(row, 4, log_item)

        self.resize_columns()

    def resize_columns(self):
        """Set column widths as percentages of table width"""
        self.table.setColumnWidth(0, int(self.table.width() * 0.15))  # Name: 15%
        self.table.setColumnWidth(1, int(self.table.width() * 0.10))  # Type: 10%
        self.table.setColumnWidth(2, int(self.table.width() * 0.35))  # Location: 35%
        self.table.setColumnWidth(3, int(self.table.width() * 0.20))  # Created: 20%
        self.table.setColumnWidth(4, int(self.table.width() * 0.20))  # Log File: 20%

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.resize_columns()

    def clean_type(self, raw_type: str) -> str:
        """Convert schema type values to user-facing labels."""
        normalized = str(raw_type).strip().lower()
        if "portfolio" in normalized:
            return "Portfolio"
        if "resume" in normalized:
            return "Resume"
        return "Unknown"

    def format_datetime(self, raw_datetime: str) -> str:
        """Format ISO datetime to a readable table value."""
        if not raw_datetime:
            return ""
        try:
            dt = datetime.fromisoformat(str(raw_datetime))
            return dt.strftime("%b %d, %Y %I:%M %p")
        except ValueError:
            return str(raw_datetime)

    def clean_log_file_name(self, raw_log_path: str) -> str:
        """Display only the log filename (e.g., 12.log)."""
        if not raw_log_path:
            return ""
        return Path(str(raw_log_path)).name

    def _open_file_in_explorer(self, file_path: Path, title: str) -> None:
        """Open Windows Explorer selecting the target file."""
        if not file_path.exists():
            QMessageBox.critical(self, "File Not Found", f"File not found:\n{file_path}")
            return

        try:
            subprocess.Popen(f'explorer /select,"{file_path}"')
        except Exception as e:
            QMessageBox.critical(self, title, f"Failed to open file location:\n{str(e)}")

    def visit_selected_backup_file(self):
        """Open Windows Explorer at the selected backup file location."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to visit.")
            return

        location_item = self.table.item(current_row, 2)
        location = location_item.data(Qt.UserRole + 1) if location_item else ""
        if not location:
            QMessageBox.warning(self, "Invalid Path", "Backup file path is empty.")
            return

        file_path = Path(location)
        self._open_file_in_explorer(file_path, "Error")

    def visit_selected_file(self):
        """Visit the original file location, with backup fallback."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to visit.")
            return

        location_item = self.table.item(current_row, 2)
        original_path = location_item.data(Qt.UserRole) if location_item else ""
        backup_path = location_item.data(Qt.UserRole + 1) if location_item else ""

        if original_path and Path(original_path).exists():
            self._open_file_in_explorer(Path(original_path), "Error")
            return

        if backup_path and Path(backup_path).exists():
            QMessageBox.information(
                self,
                "Original Not Found",
                "Original file no longer exists. Opening backup file instead.",
            )
            self._open_file_in_explorer(Path(backup_path), "Error")
            return

        QMessageBox.critical(self, "File Not Found", "Neither original nor backup file exists.")

    def visit_selected_log_file(self):
        """Open Windows Explorer at the selected log file location."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to visit.")
            return

        log_item = self.table.item(current_row, 4)
        log_path = log_item.data(Qt.UserRole) if log_item else ""
        if not log_path:
            QMessageBox.warning(self, "Invalid Path", "Log file path is empty.")
            return

        self._open_file_in_explorer(Path(log_path), "Error")

    def show_removed_items_popup(self, removed_items):
        """Show popup listing removed/invalidated items"""
        removed_names = [item.get("name", "Unknown") for item in removed_items]
        message = "The following items were removed because their files no longer exist:\n\n" + "\n".join(removed_names)

        QMessageBox.information(self, "Invalidated Items", message)