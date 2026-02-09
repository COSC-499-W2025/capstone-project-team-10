import sys
from typing import Callable, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QWidget,
)


class MultiSelector(QWidget):
    on_item_change: Optional[Callable] = None
    intro_line: str = "Select Item"

    def __init__(self):
        super().__init__()
        self.items: List[str] = []
        self.line_edit = QLineEdit()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.line_edit.setReadOnly(True)
        self.line_edit.setPlaceholderText("No Items selected")
        self.line_edit.setMinimumWidth(300)
        self.line_edit.setStyleSheet("""
            QLineEdit {
                border-radius: 4px;
                padding: 4px 8px;
            }
        """)

        self.add_button = QPushButton("+")
        self.add_button.setFixedWidth(28)
        self.add_button.setToolTip("Add Folder")
        self.add_button.setStyleSheet("""
            QPushButton {
                margin-left: 4px;
                border-radius: 4px;
                background-color: #4CAF50;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_button.clicked.connect(self.add_item)

        self.remove_button = QPushButton("-")
        self.remove_button.setFixedWidth(28)
        self.remove_button.setToolTip("Remove Item")
        self.remove_button.clicked.connect(self.remove_selected_item)
        self.remove_button.setStyleSheet("""
            QPushButton {
                border-radius: 4px;
                background-color: #e53935;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.remove_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_height = self.line_edit.sizeHint().height()
        self.add_button.setFixedHeight(button_height)
        self.remove_button.setFixedHeight(button_height)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        layout.addWidget(self.line_edit)
        layout.addStretch()
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    def add_item(self):
        item, ok = QInputDialog.getItem(
            self,
            f"Add {self.intro_line}",
            f"Add {self.intro_line}:",
            self.items,
            editable=True,
        )
        if ok and item:
            new_items = [
                i.strip().lower().replace(".", "") for i in item.split(",") if i.strip()
            ]
            self.items.extend(new_items)
            self.update_line_edit()
            if self.on_item_change:
                self.on_item_change()

    def remove_selected_item(self):
        if not self.items:
            QMessageBox.information(
                self,
                f"No {self.intro_line}",
                f"There are no {self.intro_line} to remove.",
            )
            return

        folder, ok = QInputDialog.getItem(
            self,
            f"Remove {self.intro_line}",
            f"Select a {self.intro_line} to remove:",
            self.items,
            editable=False,
        )
        if ok and folder in self.items:
            self.items.remove(folder)
            self.update_line_edit()
            if self.on_item_change:
                self.on_item_change()

    def update_line_edit(self):
        self.line_edit.setText(
            ", ".join(self.items) or f"No {self.intro_line} selected"
        )

    def set_items(self, folders: List[str]):
        self.items = folders
        self.update_line_edit()

    def get_items(self) -> List[str]:
        return self.items
