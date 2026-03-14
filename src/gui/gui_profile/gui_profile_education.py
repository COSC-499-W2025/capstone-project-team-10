from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import src.gui.gui_utils.gui_styles as styles
import src.param.param as param

# Label style
label_style = f"""
    QLabel {{
        font-weight: bold;
        font-size: 14px;
        color: #222;
        background-color: {styles.SIDEBAR_BG_COLOR};
        margin-bottom: 2px;
    }}
"""
edit_style = f"""
    QLineEdit, QTextEdit {{
        background: white;
        color: #222;
        border: 1.5px solid {styles.HEADER_BG_COLOR};
        border-radius: 5px;
        font-size: 14px;
        padding: 6px 8px;
        margin-bottom: 6px;
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 2px solid #0055aa;
        background: #f5faff;
    }}
"""
checkbox_style = f"""
    QCheckBox {{
        font-size: 13px;
        color: #222;
        padding: 6px 0 6px 4px;
        spacing: 12px;
        background-color: {styles.SIDEBAR_BG_COLOR};
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {styles.HEADER_BG_COLOR};
        border-radius: 4px;
        background: white;
    }}
    QCheckBox::indicator:unchecked {{
        background: white;
        border: 2px solid {styles.HEADER_BG_COLOR};
    }}
    QCheckBox::indicator:checked {{
        background: {styles.HEADER_BG_COLOR};
        border: 2px solid {styles.HEADER_BG_COLOR};
    }}
"""
btn_style = f"""
    QPushButton {{
        background-color: {styles.SIDEBAR_BG_COLOR};
        color: {styles.SIDEBAR_TEXT_COLOR};
        border: 1px solid {styles.HEADER_BG_COLOR};
        border-radius: 4px;
        padding: 4px 12px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {styles.SIDEBAR_ITEM_HOVER_BG};
        color: {styles.SIDEBAR_SELECTED_TEXT_COLOR};
    }}
"""


class EducationEntry(QWidget):
    def __init__(
        self,
        title: str,
        institution: str,
        location: str,
        completion_date: str,
        description: str,
        include: bool = True,
        id: int = 0,
        on_update_callback=None,
        on_remove_callback=None,
        on_move_up_callback=None,
        on_move_down_callback=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.on_update_callback = on_update_callback
        self.on_remove_callback = on_remove_callback
        self.on_move_up_callback = on_move_up_callback
        self.on_move_down_callback = on_move_down_callback
        self.id = id

        self.title_edit = QLineEdit(title)
        self.title_edit.setStyleSheet(edit_style)
        self.title_edit.textChanged.connect(self.update_self)

        self.institution_edit = QLineEdit(institution)
        self.institution_edit.setStyleSheet(edit_style)
        self.institution_edit.textChanged.connect(self.update_self)

        self.location_edit = QLineEdit(location)
        self.location_edit.setStyleSheet(edit_style)
        self.location_edit.textChanged.connect(self.update_self)

        self.completion_date_edit = QLineEdit(completion_date)
        self.completion_date_edit.setStyleSheet(edit_style)
        self.completion_date_edit.textChanged.connect(self.update_self)

        self.description_edit = QTextEdit(description)
        self.description_edit.setStyleSheet(edit_style)
        self.description_edit.textChanged.connect(self.update_self)

        self.include_checkbox = QCheckBox("Include this education entry")
        self.include_checkbox.setChecked(include)
        self.include_checkbox.setStyleSheet(checkbox_style)
        self.include_checkbox.stateChanged.connect(self.update_self)

        # Top-right controls
        control_row = QHBoxLayout()
        control_row.addStretch()

        self.up_btn = QPushButton("↑")
        self.up_btn.setStyleSheet(btn_style)
        self.up_btn.clicked.connect(
            lambda: (
                self.on_move_up_callback(self.id) if self.on_move_up_callback else None
            )
        )
        control_row.addWidget(self.up_btn)

        self.down_btn = QPushButton("↓")
        self.down_btn.setStyleSheet(btn_style)
        self.down_btn.clicked.connect(
            lambda: (
                self.on_move_down_callback(self.id)
                if self.on_move_down_callback
                else None
            )
        )
        control_row.addWidget(self.down_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet(btn_style)
        self.save_btn.clicked.connect(self.update_self)
        control_row.addWidget(self.save_btn)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setStyleSheet(btn_style)
        self.remove_btn.clicked.connect(self.delete_self)
        control_row.addWidget(self.remove_btn)

        group = QGroupBox("Education Entry")
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {styles.SIDEBAR_BG_COLOR};
                border: 2px solid {styles.HEADER_BG_COLOR};
                border-radius: 8px;
                margin-top: 12px;
                padding: 8px 8px 8px 8px;
            }}
            QGroupBox:title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {styles.HEADER_BG_COLOR};
                font-weight: bold;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        def styled_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(label_style)
            return lbl

        layout.addLayout(control_row)
        layout.addWidget(styled_label("Degree/Title:"))
        layout.addWidget(self.title_edit)
        layout.addWidget(styled_label("Institution:"))
        layout.addWidget(self.institution_edit)
        layout.addWidget(styled_label("Location:"))
        layout.addWidget(self.location_edit)
        layout.addWidget(styled_label("Completion Date:"))
        layout.addWidget(self.completion_date_edit)
        layout.addWidget(styled_label("Description:"))
        layout.addWidget(self.description_edit)
        layout.addWidget(self.include_checkbox)

        group.setLayout(layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    def update_self(self):
        if self.on_update_callback:
            self.on_update_callback()

    def delete_self(self):
        if self.on_remove_callback:
            self.on_remove_callback(self.id)

    def get_data(self):
        return {
            "title": self.title_edit.text(),
            "institution": self.institution_edit.text(),
            "location": self.location_edit.text(),
            "completion_date": self.completion_date_edit.text(),
            "description": self.description_edit.toPlainText(),
            "include": self.include_checkbox.isChecked(),
        }


class EducationProfile(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.education_layout = QGridLayout()
        self.education_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.education_layout.setHorizontalSpacing(20)
        self.education_layout.setVerticalSpacing(10)
        self.education_layout.setContentsMargins(20, 20, 20, 20)
        self.education_layout.setColumnStretch(0, 0)
        self.education_layout.setColumnStretch(1, 1)

        education_entries = param.get("profile.education") or []

        for idx, entry in enumerate(education_entries):
            item = EducationEntry(
                title=entry.get("title", ""),
                institution=entry.get("institution", ""),
                location=entry.get("location", ""),
                completion_date=entry.get("completion_date", ""),
                description=entry.get("description", ""),
                include=entry.get("include", True),
                id=idx,
                on_update_callback=self.update_education,
                on_remove_callback=self.remove_education,
                on_move_up_callback=self.move_education_up,
                on_move_down_callback=self.move_education_down,
            )
            self.education_layout.addWidget(item, idx, 0, 1, 2)

        form_container = QWidget()
        form_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_container.setLayout(self.education_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(form_container)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.add_button = QPushButton("Add Education")
        self.add_button.setStyleSheet(btn_style)
        self.add_button.clicked.connect(self.add_education)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.add_button, alignment=Qt.AlignLeft)
        main_layout.addWidget(scroll_area, stretch=1)
        main_layout.setStretch(0, 1)
        main_layout.setAlignment(form_container, Qt.AlignTop)

        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def refresh_education(self):
        for i in reversed(range(self.education_layout.count())):
            item = self.education_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        education_entries = param.get("profile.education") or []
        for idx, entry in enumerate(education_entries):
            item = EducationEntry(
                title=entry.get("title", ""),
                institution=entry.get("institution", ""),
                location=entry.get("location", ""),
                completion_date=entry.get("completion_date", ""),
                description=entry.get("description", ""),
                include=entry.get("include", True),
                id=idx,
                on_update_callback=self.update_education,
                on_remove_callback=self.remove_education,
                on_move_up_callback=self.move_education_up,
                on_move_down_callback=self.move_education_down,
            )
            self.education_layout.addWidget(item, idx, 0, 1, 2)

    def update_education(self):
        education_entries = []
        for i in range(self.education_layout.count()):
            item = self.education_layout.itemAt(i)
            if item is None:
                continue
            item_widget = item.widget()
            if isinstance(item_widget, EducationEntry):
                education_entries.append(item_widget.get_data())
        param.set("profile.education", education_entries)
        # Do not call refresh_education here to avoid recursion

    def add_education(self):
        new_entry = {
            "title": "",
            "institution": "",
            "location": "",
            "completion_date": "",
            "description": "",
            "include": False,
        }
        education_entries = param.get("profile.education") or []
        education_entries.insert(0, new_entry)  # Add new at the top
        param.set("profile.education", education_entries)
        self.refresh_education()

    def remove_education(self, index):
        education_entries = param.get("profile.education") or []
        if 0 <= index < len(education_entries):
            del education_entries[index]
            param.set("profile.education", education_entries)
            self.refresh_education()

    def move_education_up(self, index):
        education_entries = param.get("profile.education") or []
        if 1 <= index < len(education_entries):
            education_entries[index - 1], education_entries[index] = (
                education_entries[index],
                education_entries[index - 1],
            )
            param.set("profile.education", education_entries)
            self.refresh_education()

    def move_education_down(self, index):
        education_entries = param.get("profile.education") or []
        if 0 <= index < len(education_entries) - 1:
            education_entries[index + 1], education_entries[index] = (
                education_entries[index],
                education_entries[index + 1],
            )
            param.set("profile.education", education_entries)
            self.refresh_education()
