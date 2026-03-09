from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
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
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Git username
        self.git_user = QLineEdit(param.get("scan.github_username"))
        self.git_user.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Git username:", self.git_user)
        self.git_user.editingFinished.connect(self.update_git_username)

        # Scan hidden files (button-like toggle)
        self.hidden_files = QCheckBox("Off")
        self.hidden_files.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.hidden_files.setFixedHeight(self.git_user.sizeHint().height() + 12)  # taller than before
        self.hidden_files.setCursor(Qt.PointingHandCursor)
        self.hidden_files.setStyleSheet("""
            QCheckBox {
                border: 1px solid #8c8c8c;
                border-radius: 6px;
                background: #f2f2f2;
                font-weight: 600;
                padding: 0px 8px;
                text-align: center;
                spacing: 0px;
            }
            QCheckBox::indicator {
                width: 0px;   /* hide checkbox square */
                height: 0px;
            }
            QCheckBox:checked {
                background: #002145;
                color: white;
                border: 1px solid #002145;
            }
        """)

        if str(param.get("scan.scan_hidden_files")).strip().lower() in ("true", "1", "yes", "on"):
            self.hidden_files.setChecked(True)
            self.hidden_files.setText("On")
        else:
            self.hidden_files.setChecked(False)
            self.hidden_files.setText("Off")

        # Delay until widget is fully polished/la[id] out
        QTimer.singleShot(0, self._fit_hidden_files_button_width)

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
        form_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        main_layout = QVBoxLayout()
        main_layout.addWidget(form_container)
        self.setLayout(main_layout)

        self._normalize_selector_buttons()

    def _normalize_selector_buttons(self):
        for selector in (self.file_types_for_scan, self.ignore_file_types, self.exclude_folders):
            for btn in selector.findChildren(QPushButton):
                txt = btn.text().strip()
                if txt in {"+", "＋"}:
                    btn.setText("+")
                    btn.setFixedSize(28, 28)
                    btn.setContentsMargins(0, 0, 0, 0)
                    btn.setStyleSheet("""
                        QPushButton {
                            padding: 0px;
                            margin: 0px;
                            text-align: center;
                            font-weight: bold;
                            color: #1f6f3d;
                            background-color: #bfeecf;
                            border: 1px solid #8fd6ad;
                            border-radius: 4px;
                        }
                        QPushButton:hover { background-color: #aee5c2; }
                        QPushButton:pressed { background-color: #9bdcb6; }
                    """)
                elif txt in {"-", "－"}:
                    btn.setText("-")
                    btn.setFixedSize(28, 28)
                    btn.setContentsMargins(0, 0, 0, 0)
                    btn.setStyleSheet("""
                        QPushButton {
                            padding: 0px;
                            margin: 0px;
                            text-align: center;
                            font-weight: bold;
                            color: #8a2f3d;
                            background-color: #f7c8cf;
                            border: 1px solid #e5a1ac;
                            border-radius: 4px;
                        }
                        QPushButton:hover { background-color: #f2b7c0; }
                        QPushButton:pressed { background-color: #eda6b1; }
                    """)

    def update_git_username(self):
        new_username = self.git_user.text()
        if not param.set("scan.github_username", new_username):
            param.set("scan.github_username", "")
        self.git_user.setText(param.get("scan.github_username"))

    def _fit_hidden_files_button_width(self):
        self.hidden_files.adjustSize()
        self.hidden_files.setFixedWidth(self.hidden_files.sizeHint().width() + 6)

    def update_hidden_files(self):
        new_value = self.hidden_files.isChecked()
        if new_value:
            self.hidden_files.setText("On")
        else:
            self.hidden_files.setText("Off")
        self._fit_hidden_files_button_width()
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
