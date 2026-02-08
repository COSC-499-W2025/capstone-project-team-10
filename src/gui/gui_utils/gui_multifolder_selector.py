import sys
from typing import Callable, List, Optional

from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QWidget,
)


class MultiFolderSelector(QWidget):
    on_folder_change: Optional[Callable] = None

    def __init__(self):
        super().__init__()
        self.items: List[str] = []
        self.line_edit = QLineEdit()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.line_edit.setReadOnly(True)
        self.line_edit.setPlaceholderText("No folders selected")
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
        self.add_button.clicked.connect(self.add_folder)

        self.remove_button = QPushButton("-")
        self.remove_button.setFixedWidth(28)
        self.remove_button.setToolTip("Remove Item")
        self.remove_button.clicked.connect(self.remove_selected_folder)
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

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        print(f"Selected folder: {folder}")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.update_line_edit()
            if self.on_folder_change:
                self.on_folder_change()

    def remove_last_folder(self):
        if self.folders:
            self.folders.pop()
            self.update_line_edit()
            if self.on_folder_change:
                self.on_folder_change()
        else:
            QMessageBox.information(
                self, "No folders", "There are no folders to remove."
            )

    def remove_selected_folder(self):
        if not self.folders:
            QMessageBox.information(
                self, "No folders", "There are no folders to remove."
            )
            return

        folder, ok = QInputDialog.getItem(
            self,
            "Remove Folder",
            "Select a folder to remove:",
            self.folders,
            editable=False,
        )
        if ok and folder in self.folders:
            self.folders.remove(folder)
            self.update_line_edit()
            if self.on_folder_change:
                self.on_folder_change()

    def update_line_edit(self):
        self.line_edit.setText(", ".join(self.folders) or "No folders selected")

    def set_folders(self, folders: List[str]):
        self.folders = folders
        self.update_line_edit()

    def get_folders(self) -> List[str]:
        return self.folders
