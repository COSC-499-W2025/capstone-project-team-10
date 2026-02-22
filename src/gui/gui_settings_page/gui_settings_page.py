from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import src.param.param as param
from src.gui.gui_settings_page.gui_settings_logs import LoggingPage
from src.gui.gui_settings_page.gui_settings_scan import ScanPage
from src.gui.gui_settings_page.gui_settings_showcase import ShowcasePage

# ---------- UI Color Constants ----------
HEADER_BG_COLOR = "#002145"

SIDEBAR_BG_COLOR = "#B1B2B5"
SIDEBAR_ITEM_SELECTED_BG = "#616264"
SIDEBAR_ITEM_HOVER_BG = "rgba(97, 98, 100, 120)"

SIDEBAR_TEXT_COLOR = "black"
SIDEBAR_SELECTED_TEXT_COLOR = "white"


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItems(["Scan", "Logging", "Showcase"])
        self.sidebar.currentRowChanged.connect(self.display_page)
        self.sidebar.setMaximumWidth(150)
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                padding: 5px;
                margin: 0px;
                background-color: {SIDEBAR_BG_COLOR};
                color: {SIDEBAR_TEXT_COLOR};
            }}
            QListWidget::item:selected {{
                background-color: {SIDEBAR_ITEM_SELECTED_BG};  
                color: {SIDEBAR_SELECTED_TEXT_COLOR};
            }}
            QListWidget::item {{
                    padding: 8px 0;
                    margin-bottom: 4px;
                    border-radius: 6px;
            }}
        """)

        self.pages = QStackedWidget()
        self.pages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pages.addWidget(ScanPage())
        self.pages.addWidget(LoggingPage())
        self.pages.addWidget(ShowcasePage())
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
