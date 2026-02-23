from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
import subprocess
import os
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

        layout.addWidget(self.table, 1)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.visit_btn = QPushButton("Visit File")
        self.visit_btn.clicked.connect(self.visit_selected_file)

        button_layout.addStretch()
        button_layout.addWidget(self.visit_btn)

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
            file_path = item.get("path", "")
            if file_path and Path(file_path).exists():
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
            file_type = item.get("type", "")
            location = item.get("path", "")
            created = item.get("created_at", "")
            log_file = item.get("log", "")

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(file_type))
            self.table.setItem(row, 2, QTableWidgetItem(location))
            self.table.setItem(row, 3, QTableWidgetItem(created))
            self.table.setItem(row, 4, QTableWidgetItem(log_file))

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

    def visit_selected_file(self):
        """Open Windows Explorer at the selected file's location"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to visit.")
            return

        location = self.table.item(current_row, 2).text()
        if not location:
            QMessageBox.warning(self, "Invalid Path", "File path is empty.")
            return

        file_path = Path(location)
        if not file_path.exists():
            QMessageBox.critical(self, "File Not Found", f"File not found:\n{location}")
            return

        # Open Windows Explorer at the file location
        try:
            subprocess.Popen(f'explorer /select,"{file_path}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file location:\n{str(e)}")

    def show_removed_items_popup(self, removed_items):
        """Show popup listing removed/invalidated items"""
        removed_names = [item.get("name", "Unknown") for item in removed_items]
        message = "The following items were removed because their files no longer exist:\n\n" + "\n".join(removed_names)

        QMessageBox.information(self, "Invalidated Items", message)