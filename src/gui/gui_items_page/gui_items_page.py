from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from datetime import datetime
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
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.horizontalHeader().setFixedHeight(34)
        self.table.setStyleSheet(
            ""
            "QTableWidget::item:focus { outline: none; }"
            "QHeaderView::section {"
            "background-color: #f3f3f3;"
            "border-top: 1px solid #d9d9d9;"
            "border-bottom: 1px solid #d9d9d9;"
            "border-right: 1px solid #d9d9d9;"
            "border-left: 0px;"
            "padding-top: 2px;"
            "padding-bottom: 2px;"
            "}"
            "QHeaderView::section:first {"
            "border-left: 1px solid #d9d9d9;"
            "}"
            ""
        )

        # Keep headers visually consistent regardless of selection state.
        for col in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col)
            if header_item is not None:
                header_font = header_item.font()
                header_font.setBold(True)
                header_item.setFont(header_font)

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

            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, item.get("id"))
            self.table.setItem(row, 0, name_item)
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
        """Open the file location in the platform file manager."""
        if not file_path.exists():
            QMessageBox.critical(self, "File Not Found", f"File not found:\n{file_path}")
            return

        try:
            folder_path = file_path.resolve().parent
            opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))
            if not opened:
                raise RuntimeError(f"Could not open folder: {folder_path}")
        except Exception as e:
            QMessageBox.critical(self, title, f"Failed to open file location:\n{str(e)}")

    def _delete_entry_by_id(self, item_id) -> bool:
        items = self.manager.load_items()
        filtered = [item for item in items if item.get("id") != item_id]
        if len(filtered) == len(items):
            return False
        self.manager.save_items(filtered)
        return True

    def _prompt_delete_if_both_missing(self, row: int) -> None:
        name_item = self.table.item(row, 0)
        item_name = name_item.text() if name_item else "this item"
        item_id = name_item.data(Qt.UserRole) if name_item else None

        reply = QMessageBox.question(
            self,
            "Files Missing",
            f"Both downloaded/original and backup files are missing for '{item_name}'.\n\n"
            "Do you want to delete this entry from the list?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        if item_id is None:
            QMessageBox.warning(
                self,
                "Delete Failed",
                "Could not identify the selected entry.",
            )
            return

        if self._delete_entry_by_id(item_id):
            QMessageBox.information(self, "Entry Deleted", f"Deleted '{item_name}' from the list.")
            self.load_and_validate_items()
        else:
            QMessageBox.warning(self, "Delete Failed", f"Could not delete '{item_name}'.")

    def visit_selected_backup_file(self):
        """Open the selected backup file location, with original fallback if needed."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to visit.")
            return

        location_item = self.table.item(current_row, 2)
        original_path = location_item.data(Qt.UserRole) if location_item else ""
        backup_path = location_item.data(Qt.UserRole + 1) if location_item else ""

        original_exists = bool(original_path) and Path(original_path).exists()
        backup_exists = bool(backup_path) and Path(backup_path).exists()

        if backup_exists:
            self._open_file_in_explorer(Path(backup_path), "Error")
            return

        if original_exists:
            reply = QMessageBox.question(
                self,
                "Backup File Missing",
                "Backup file is missing.\n\nOpen the downloaded/original file instead?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                self._open_file_in_explorer(Path(original_path), "Error")
            return

        self._prompt_delete_if_both_missing(current_row)

    def visit_selected_file(self):
        """Visit the original file location, with backup fallback."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to visit.")
            return

        location_item = self.table.item(current_row, 2)
        original_path = location_item.data(Qt.UserRole) if location_item else ""
        backup_path = location_item.data(Qt.UserRole + 1) if location_item else ""

        original_exists = bool(original_path) and Path(original_path).exists()
        backup_exists = bool(backup_path) and Path(backup_path).exists()

        if original_exists:
            self._open_file_in_explorer(Path(original_path), "Error")
            return

        if backup_exists:
            reply = QMessageBox.question(
                self,
                "Downloaded File Missing",
                "Downloaded/original file is missing.\n\nOpen backup file instead?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                self._open_file_in_explorer(Path(backup_path), "Error")
            return

        self._prompt_delete_if_both_missing(current_row)

    def visit_selected_log_file(self):
        """Open the selected log file location."""
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