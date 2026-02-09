from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import src.gui.gui_utils.gui_styles as styles
import src.param.param as param


class ShowcasePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        form_layout = QFormLayout()
        form_layout.setAlignment(Qt.AlignLeft)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setMaximumWidth(3000)

        self.folder_line_edit = QLineEdit(param.get("showcase.showcase_export_path"))
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.folder_line_edit.editingFinished.connect(self.update_showcase_export_path)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_line_edit)
        folder_layout.addWidget(self.select_folder_btn, alignment=Qt.AlignVCenter)

        form_layout.addRow("Showcase save location:", folder_layout)

        self.max_showcase_length = QLineEdit()
        form_layout.addRow(
            "Maximum Showcase Length In Entries", self.max_showcase_length
        )
        self.max_showcase_length.setText(
            str(param.get("showcase.showcase_maximum_exports"))
        )
        self.max_showcase_length.editingFinished.connect(
            self.update_max_showcase_length
        )

        main_layout = QVBoxLayout()
        main_layout.addWidget(form_container)
        main_layout.setAlignment(form_container, Qt.AlignLeft | Qt.AlignTop)

        self.setLayout(main_layout)

    def update_showcase_export_path(self):
        new_path = self.folder_line_edit.text().strip()
        if new_path:
            if Path(new_path).is_dir():
                param.set("showcase.showcase_export_path", new_path)
                self.folder_line_edit.setText(
                    param.get("showcase.showcase_export_path")
                )

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_line_edit.setText(folder)
            self.update_showcase_export_path()

    def update_max_showcase_length(self):
        new_length = self.max_showcase_length.text().strip()
        if new_length.isdigit():
            param.set("showcase.showcase_maximum_exports", int(new_length))
        else:
            self.max_showcase_length.setText(
                str(param.get("showcase.showcase_maximum_exports"))
            )
