from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import src.gui.gui_utils.gui_styles as styles
import src.param.param as param
from src.gui.gui_utils.gui_multifolder_selector import MultiFolderSelector
from src.gui.gui_utils.gui_multiselector import MultiSelector

""" Work experience data structure example:
{
    "company": "The Clown Factory",
    "position": "Head Clown",
    "location": "University of British Columbia",
    "date_start": "Birth",
    "date_end": "Death",
    "description": "Head clown at the clown factory, responsible for overseeing all clowning activities and ensuring the success of each performance.",
    "responsibilities": [
        "Overseeing clowning activities",
        "Coordinating performances",
        "Managing the clown team"
    ],
    "include": true
},"""

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
# LineEdit and QTextEdit style
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

# Checkbox style (native indicator, just text and spacing)
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

# Remove button style
remove_btn_style = """
    QPushButton {
        background: #fff0f0;
        color: #a00;
        border: 1px solid #a00;
        border-radius: 4px;
        padding: 2px 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background: #ffeaea;
        color: #fff;
        border: 1.5px solid #d00;
    }
"""
# Button style
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


class WorkExperienceItem(QWidget):
    def __init__(
        self,
        company: str,
        position: str,
        location: str,
        date_start: str,
        date_end: str,
        description: str,
        responsibilities: list = [],
        include: bool = True,
        id: float = 0,
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
        self.company_edit = QLineEdit(company)
        self.company_edit.setStyleSheet(edit_style)

        self.position_edit = QLineEdit(position)
        self.position_edit.setStyleSheet(edit_style)

        self.location_edit = QLineEdit(location)
        self.location_edit.setStyleSheet(edit_style)

        self.date_start_edit = QLineEdit(date_start)
        self.date_start_edit.setStyleSheet(edit_style)

        self.date_end_edit = QLineEdit(date_end)
        self.date_end_edit.setStyleSheet(edit_style)

        self.description_edit = QTextEdit(description)
        self.description_edit.setStyleSheet(edit_style)

        self.include_checkbox = QCheckBox("Include this experience")
        self.include_checkbox.setChecked(include)
        self.include_checkbox.setStyleSheet(checkbox_style)
        self.include_checkbox.stateChanged.connect(self.update_self)

        # Responsibilities list
        self.responsibilities_list = QListWidget()
        for resp in responsibilities:
            self.responsibilities_list.addItem(QListWidgetItem(resp))

        # Add/Remove responsibility controls
        resp_input_layout = QHBoxLayout()
        self.resp_input = QLineEdit()
        self.resp_input.setPlaceholderText("Add responsibility...")
        self.resp_add_btn = QPushButton("Add")
        self.resp_add_btn.setStyleSheet(btn_style)
        self.resp_add_btn.clicked.connect(self.add_responsibility)
        self.resp_remove_btn = QPushButton("Remove Selected")
        self.resp_remove_btn.setStyleSheet(btn_style)
        self.resp_remove_btn.clicked.connect(self.remove_selected_responsibility)
        resp_input_layout.addWidget(self.resp_input)
        resp_input_layout.addWidget(self.resp_add_btn)
        resp_input_layout.addWidget(self.resp_remove_btn)

        remove_row = QHBoxLayout()
        remove_row.addStretch()

        self.up_btn = QPushButton("↑")
        self.up_btn.setStyleSheet(btn_style)
        self.up_btn.clicked.connect(self.move_up)
        remove_row.addWidget(self.up_btn)

        self.down_btn = QPushButton("↓")
        self.down_btn.setStyleSheet(btn_style)
        self.down_btn.clicked.connect(self.move_down)
        remove_row.addWidget(self.down_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet(btn_style)
        self.save_btn.clicked.connect(self.update_self)
        remove_row.addWidget(self.save_btn)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setStyleSheet(btn_style)
        self.remove_btn.clicked.connect(self.delete_self)
        remove_row.addWidget(self.remove_btn)

        work_group = QGroupBox("Experience")
        work_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        work_group.setStyleSheet(f"""
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

        work_layout = QVBoxLayout()
        work_layout.setContentsMargins(16, 16, 16, 16)
        work_layout.setSpacing(8)

        def styled_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(label_style)
            return lbl

        work_layout.addLayout(remove_row)
        work_layout.addWidget(styled_label("Company:"))
        work_layout.addWidget(self.company_edit)
        work_layout.addWidget(styled_label("Position:"))
        work_layout.addWidget(self.position_edit)
        work_layout.addWidget(styled_label("Location:"))
        work_layout.addWidget(self.location_edit)
        work_layout.addWidget(styled_label("Start Date:"))
        work_layout.addWidget(self.date_start_edit)
        work_layout.addWidget(styled_label("End Date:"))
        work_layout.addWidget(self.date_end_edit)
        work_layout.addWidget(styled_label("Description:"))
        work_layout.addWidget(self.description_edit)
        work_layout.addWidget(styled_label("Responsibilities:"))
        work_layout.addWidget(self.responsibilities_list)
        work_layout.addLayout(resp_input_layout)
        work_layout.addWidget(self.include_checkbox)

        work_group.setLayout(work_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(work_group)
        self.setLayout(main_layout)

    def add_responsibility(self):
        text = self.resp_input.text().strip()
        if text:
            self.responsibilities_list.addItem(QListWidgetItem(text))
            self.resp_input.clear()
            self.update_self()

    def remove_selected_responsibility(self):
        for item in self.responsibilities_list.selectedItems():
            self.responsibilities_list.takeItem(self.responsibilities_list.row(item))
        self.update_self()

    def move_up(self):
        if self.on_move_up_callback:
            self.on_move_up_callback(self.id)

    def move_down(self):
        if self.on_move_down_callback:
            self.on_move_down_callback(self.id)

    def update_self(self):
        if self.on_update_callback:
            self.on_update_callback()

    def delete_self(self):
        if self.on_remove_callback:
            self.on_remove_callback(self.id)

    def get_data(self):
        """Return the current state as a dict."""
        responsibilities = []
        for i in range(self.responsibilities_list.count()):
            item = self.responsibilities_list.item(i)
            if item is not None:
                responsibilities.append(item.text())

        return {
            "company": self.company_edit.text(),
            "position": self.position_edit.text(),
            "location": self.location_edit.text(),
            "date_start": self.date_start_edit.text(),
            "date_end": self.date_end_edit.text(),
            "description": self.description_edit.toPlainText(),
            "responsibilities": responsibilities,
            "include": self.include_checkbox.isChecked(),
        }


class WorkProfile(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.experience_layout = QGridLayout()
        self.experience_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.experience_layout.setHorizontalSpacing(20)
        self.experience_layout.setVerticalSpacing(10)
        self.experience_layout.setContentsMargins(20, 20, 20, 20)

        # Set column stretch: labels (col 0) minimal, fields (col 1) expand
        self.experience_layout.setColumnStretch(0, 0)
        self.experience_layout.setColumnStretch(1, 1)

        work_experiences = param.get("profile.work_experience")

        if work_experiences:
            for idx, exp in enumerate(work_experiences):
                item = WorkExperienceItem(
                    company=exp.get("company", ""),
                    position=exp.get("position", ""),
                    location=exp.get("location", ""),
                    date_start=exp.get("date_start", ""),
                    date_end=exp.get("date_end", ""),
                    description=exp.get("description", ""),
                    responsibilities=exp.get("responsibilities", []),
                    include=exp.get("include", True),
                    id=idx,
                    on_update_callback=self.update_work_experience,
                    on_remove_callback=self.remove_work_experience,
                    on_move_up_callback=self.move_experience_up,
                    on_move_down_callback=self.move_experience_down,
                )
                self.experience_layout.addWidget(item, idx, 0, 1, 2)

        form_container = QWidget()
        form_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_container.setLayout(self.experience_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(form_container)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.add_button = QPushButton("Add Experience")
        self.add_button.setStyleSheet(btn_style)
        self.add_button.clicked.connect(self.add_work_experience)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.add_button, alignment=Qt.AlignLeft)
        main_layout.addWidget(scroll_area, stretch=1)
        main_layout.setStretch(0, 1)
        main_layout.setAlignment(form_container, Qt.AlignTop)

        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def refresh_experiences(self):
        # Clear existing items
        for i in reversed(range(self.experience_layout.count())):
            item = self.experience_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        # Re-add items from param
        work_experiences = param.get("profile.work_experience") or []
        for idx, exp in enumerate(work_experiences):
            item = WorkExperienceItem(
                company=exp.get("company", ""),
                position=exp.get("position", ""),
                location=exp.get("location", ""),
                date_start=exp.get("date_start", ""),
                date_end=exp.get("date_end", ""),
                description=exp.get("description", ""),
                responsibilities=exp.get("responsibilities", []),
                include=exp.get("include", True),
                id=idx,
                on_update_callback=self.update_work_experience,
                on_remove_callback=self.remove_work_experience,
                on_move_up_callback=self.move_experience_up,
                on_move_down_callback=self.move_experience_down,
            )
            self.experience_layout.addWidget(item, idx, 0, 1, 2)

    def update_work_experience(self):
        work_experiences = []
        for i in range(self.experience_layout.count()):
            item = self.experience_layout.itemAt(i)
            if item is None:
                continue
            item_widget = item.widget()
            if isinstance(item_widget, WorkExperienceItem):
                work_experiences.append(item_widget.get_data())
        param.set("profile.work_experience", work_experiences)
        self.refresh_experiences()

    def add_work_experience(self):
        new_exp = {
            "company": "",
            "position": "",
            "location": "",
            "date_start": "",
            "date_end": "",
            "description": "",
            "responsibilities": [],
            "include": False,
        }
        work_experiences = param.get("profile.work_experience") or []
        work_experiences.insert(0, new_exp)
        param.set("profile.work_experience", work_experiences)
        self.refresh_experiences()

    def remove_work_experience(self, index):
        work_experiences = param.get("profile.work_experience") or []
        if 0 <= index < len(work_experiences):
            del work_experiences[index]
            param.set("profile.work_experience", work_experiences)
            self.refresh_experiences()

    def move_experience_up(self, index):
        work_experiences = param.get("profile.work_experience") or []
        if 1 <= index < len(work_experiences):
            work_experiences[index - 1], work_experiences[index] = (
                work_experiences[index],
                work_experiences[index - 1],
            )
            param.set("profile.work_experience", work_experiences)
            self.refresh_experiences()

    def move_experience_down(self, index):
        work_experiences = param.get("profile.work_experience") or []
        if 0 <= index < len(work_experiences) - 1:
            work_experiences[index + 1], work_experiences[index] = (
                work_experiences[index],
                work_experiences[index + 1],
            )
            param.set("profile.work_experience", work_experiences)
            self.refresh_experiences()
