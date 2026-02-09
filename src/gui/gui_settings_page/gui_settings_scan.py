from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QLineEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import src.gui.gui_utils.gui_styles as styles
import src.param.param as param
from src.gui.gui_utils.gui_multifolder_selector import MultiFolderSelector
from src.gui.gui_utils.gui_multiselector import MultiSelector


class ScanPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        form_layout = QFormLayout()
        form_layout.setAlignment(Qt.AlignLeft)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # Git username
        self.git_user = QLineEdit(param.get("scan.github_username"))
        form_layout.addRow("Git username:", self.git_user)
        self.git_user.editingFinished.connect(self.update_git_username)

        # Scan hidden files
        self.hidden_files = QCheckBox("Off")
        self.hidden_files.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.hidden_files.setStyleSheet(f"""
            QCheckBox{{
                border-radius: 4px;
                border: 1px solid black;
                background-color: {styles.SIDEBAR_BG_COLOR};    
            }}
        """)
        if str(param.get("scan.scan_hidden_files")).strip().lower() in (
            "true",
            "1",
            "yes",
            "on",
        ):
            self.hidden_files.setChecked(True)
            self.hidden_files.setText("On")
        else:
            self.hidden_files.setChecked(False)
            self.hidden_files.setText("Off")
        form_layout.addRow("Scan hidden files?", self.hidden_files)
        self.hidden_files.stateChanged.connect(self.update_hidden_files)

        # File types for scan
        self.file_types_for_scan = MultiSelector()
        self.file_types_for_scan.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.file_types_for_scan.intro_line = "Scan File types"
        self.file_types_for_scan.set_items(param.get("scan.supported_file_types") or [])
        form_layout.addRow("Scan File types:", self.file_types_for_scan)
        self.file_types_for_scan.on_item_change = self.update_file_types_for_scan

        # Ignore file types
        self.ignore_file_types = MultiSelector()
        self.ignore_file_types.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ignore_file_types.intro_line = "Ignore File types"
        self.ignore_file_types.set_items(param.get("scan.excluded_file_types") or [])
        form_layout.addRow("Ignore File types:", self.ignore_file_types)
        self.ignore_file_types.on_item_change = self.update_ignored_file_types

        # Exclude folders
        self.exclude_folders = MultiFolderSelector()
        self.exclude_folders.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.exclude_folders.intro_line = "Exclude Folders"
        self.exclude_folders.set_folders(param.get("scan.excluded_file_paths") or [])
        form_layout.addRow("Exclude Folders", self.exclude_folders)
        self.exclude_folders.on_folder_change = self.update_excluded_folders

        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setMaximumWidth(3000)

        main_layout = QVBoxLayout()
        main_layout.addWidget(form_container)
        main_layout.setAlignment(form_container, Qt.AlignLeft | Qt.AlignTop)

        self.setLayout(main_layout)

    def update_git_username(self):
        new_username = self.git_user.text()
        if not param.set("scan.github_username", new_username):
            param.set("scan.github_username", "")
        self.git_user.setText(param.get("scan.github_username"))

    def update_hidden_files(self):
        new_value = self.hidden_files.isChecked()
        if new_value:
            self.hidden_files.setText("On")
        else:
            self.hidden_files.setText("Off")
        if not param.set("scan.scan_hidden_files", new_value):
            print("Failed to update scan hidden files in settings manager")

    def update_file_types_for_scan(self):
        if not param.set(
            "scan.supported_file_types", self.file_types_for_scan.get_items()
        ):
            print("Failed to update file types for scan in settings manager")

    def update_ignored_file_types(self):
        if not param.set(
            "scan.excluded_file_types", self.ignore_file_types.get_items()
        ):
            print("Failed to update ignored file types in settings manager")

    def update_excluded_folders(self):
        print("Excluded folders updated:", self.exclude_folders.get_folders())
        if not param.set(
            "scan.excluded_file_paths", self.exclude_folders.get_folders()
        ):
            print("Failed to update excluded folders in settings manager")
