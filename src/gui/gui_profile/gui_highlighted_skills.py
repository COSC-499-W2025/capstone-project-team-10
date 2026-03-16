from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import src.gui.gui_utils.gui_styles as styles
import src.param.param as param
from src.gui.gui_utils.gui_multifolder_selector import MultiFolderSelector
from src.gui.gui_utils.gui_multiselector import MultiSelector


class SkillListItem(QWidget):
    def __init__(self, skill_name, checked=True, remove_callback=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)  # More padding for clarity
        layout.setSpacing(12)

        self.checkbox = QCheckBox("Include: " + skill_name)
        self.checkbox.setChecked(checked)
        self.checkbox.setStyleSheet(f"""
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
        """)  # No indicator styling, keeps native look

        layout.addWidget(self.checkbox)

        self.remove_button = QPushButton("Remove")
        self.remove_button.setMinimumWidth(60)
        self.remove_button.setMaximumWidth(80)
        self.remove_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.remove_button.setStyleSheet(f"""
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
        """)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)
        self.setStyleSheet(f"""
            background-color: {styles.SIDEBAR_BG_COLOR};
            border-bottom: 1px solid {styles.HEADER_BG_COLOR};
        """)

        if remove_callback:
            self.remove_button.clicked.connect(remove_callback)


class HighlightedSkills(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        grid_layout = QGridLayout()
        grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)
        grid_layout.setContentsMargins(20, 20, 20, 20)

        # Set column stretch: labels (col 0) minimal, fields (col 1) expand
        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 1)

        # Highlighted skills
        skills_group = QGroupBox("Highlighted Skills")
        skills_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        skills_group.setStyleSheet(f"""
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

        skills_layout = QVBoxLayout()
        skills_layout.setContentsMargins(16, 16, 16, 16)
        skills_layout.setSpacing(8)

        self.highlighted_skills = QListWidget()
        # self.highlighted_skills.setMaximumHeight(360)
        self.highlighted_skills.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.highlighted_skills.setStyleSheet(f"""
            QListWidget {{
                background: white;
                border: 1px solid {styles.HEADER_BG_COLOR};
                border-radius: 4px;
                padding: 8px;
            }}
        """)

        skills = param.get("profile.highlighted_skills") or []
        for skill in skills:
            self.add_skill_widget(skill.get("skill", ""), skill.get("include", True))
        self.highlighted_skills.itemChanged.connect(self.update_highlighted_skills)

        add_skill_layout = QHBoxLayout()
        add_skill_layout.setContentsMargins(0, 8, 0, 0)  # Padding above the add row
        add_skill_layout.setSpacing(8)

        self.add_skill_input = QLineEdit()
        self.add_skill_input.setPlaceholderText("Add a new skill...")
        self.add_skill_input.setStyleSheet(f"""
            QLineEdit {{
                background: white;
                border: 1px solid {styles.HEADER_BG_COLOR};
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """)

        self.add_skill_button = QPushButton("Add")
        self.add_skill_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.add_skill_button.setMinimumWidth(60)
        self.add_skill_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.SIDEBAR_BG_COLOR};
                color: {styles.SIDEBAR_TEXT_COLOR};
                border: 1px solid {styles.HEADER_BG_COLOR};
                border-radius: 4px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background-color: {styles.SIDEBAR_ITEM_HOVER_BG};
                color: {styles.SIDEBAR_SELECTED_TEXT_COLOR};
            }}
        """)
        self.add_skill_button.clicked.connect(self.add_skill_to_list)
        add_skill_layout.addWidget(self.add_skill_input, stretch=1)
        add_skill_layout.addWidget(self.add_skill_button)

        skills_layout.addWidget(self.highlighted_skills)
        skills_layout.addLayout(add_skill_layout)
        skills_group.setLayout(skills_layout)
        grid_layout.addWidget(skills_group, 0, 0, 1, 2)

        form_container = QWidget()
        form_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_container.setLayout(grid_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(form_container, stretch=1)
        main_layout.setStretch(0, 1)
        main_layout.setAlignment(form_container, Qt.AlignTop)

        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def add_skill_widget(self, skill_text, checked=True):
        item = QListWidgetItem()
        widget = SkillListItem(
            skill_text, checked, remove_callback=lambda: self.remove_skill(item)
        )
        item.setSizeHint(widget.sizeHint())
        self.highlighted_skills.addItem(item)
        self.highlighted_skills.setItemWidget(item, widget)
        widget.checkbox.stateChanged.connect(self.update_highlighted_skills)

    def remove_skill(self, item):
        row = self.highlighted_skills.row(item)
        self.highlighted_skills.takeItem(row)
        self.update_highlighted_skills()

    def add_skill_to_list(self):
        skill_text = self.add_skill_input.text().strip()
        if skill_text:
            self.add_skill_widget(skill_text, checked=True)
            self.add_skill_input.clear()
            self.update_highlighted_skills()

    def update_highlighted_skills(self):
        skills = []
        for i in range(self.highlighted_skills.count()):
            item = self.highlighted_skills.item(i)
            widget = self.highlighted_skills.itemWidget(item)
            if widget:
                skills.append(
                    {
                        "skill": widget.checkbox.text(),
                        "include": widget.checkbox.isChecked(),
                    }
                )
        param.set("profile.highlighted_skills", skills)
