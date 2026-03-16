from PyQt5.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import src.gui.gui_utils.gui_styles as styles
from src.gui.gui_profile.gui_highlighted_skills import HighlightedSkills
from src.gui.gui_profile.gui_personal_profile import PersonalProfile
from src.gui.gui_profile.gui_profile_awards import AwardsProfile
from src.gui.gui_profile.gui_profile_education import EducationProfile
from src.gui.gui_profile.gui_work_experience import WorkProfile


class ProfilePage(QWidget):
    def __init__(self):
        super().__init__()

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItems(
            ["Personal Profile", "Skills", "Work Experience", "Education", "Awards"]
        )
        self.sidebar.currentRowChanged.connect(self.display_page)
        self.sidebar.setMaximumWidth(150)
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                padding: 5px;
                margin: 0px;
                background-color: {styles.SIDEBAR_BG_COLOR};
                color: {styles.SIDEBAR_TEXT_COLOR};
            }}
            QListWidget::item:selected {{
                background-color: {styles.SIDEBAR_ITEM_SELECTED_BG};  
                color: {styles.SIDEBAR_SELECTED_TEXT_COLOR};
            }}
            QListWidget::item {{
                    padding: 8px 0;
                    margin-bottom: 4px;
                    border-radius: 6px;
            }}
        """)

        self.pages = QStackedWidget()
        self.pages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.pages.addWidget(PersonalProfile())
        self.pages.addWidget(HighlightedSkills())
        self.pages.addWidget(WorkProfile())
        self.pages.addWidget(EducationProfile())
        self.pages.addWidget(AwardsProfile())
        self.pages.setStyleSheet("""
            QStackedWidget {
                background-color: white;
                border: none;
                padding: 20px;
            }
            QWidget {
                background-color: white;
                color: black;
                font-size: 14px;
            }
            QTextEdit, QLineEdit {
                border: 1px solid #ccc;
                text-align: left;
                border-radius: 4px;
                padding: 6px;
            }
                QLineEdit:focus, QTextEdit:focus {
                border-color: #66afe9;
                outline: none;
            }
        """)

        # Layout
        layout = QHBoxLayout()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove all padding
        layout.setSpacing(0)
        self.setLayout(layout)
        self.sidebar.setCurrentRow(0)

    def display_page(self, index):
        self.pages.setCurrentIndex(index)
