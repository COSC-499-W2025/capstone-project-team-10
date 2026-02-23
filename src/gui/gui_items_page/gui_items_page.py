from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from .gui_items_manager import GuiItemsManager


class ItemsPage(QWidget):
    """GUI page for viewing generated items."""

    def __init__(self):
        super().__init__()
        self.manager = GuiItemsManager()
        self.init_ui()
        self.load_items_table()

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

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_items_table)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected_item)

        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

    def load_items_table(self):
        """Load items from manager and populate table"""
        items = self.manager.load_items()
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

    def delete_selected_item(self):
        """Delete the selected item"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this item?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.manager.delete_item(current_row):
                self.load_items_table()
                QMessageBox.information(self, "Success", "Item deleted successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete item.")