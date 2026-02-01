from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget
)
from PyQt5.QtCore import Qt
from src.gui.gui_scan_page import ScanPage

# ---------- UI Color Constants ----------
HEADER_BG_COLOR = "#002145"

SIDEBAR_BG_COLOR = "#B1B2B5"
SIDEBAR_ITEM_SELECTED_BG = "#616264"
SIDEBAR_ITEM_HOVER_BG = "rgba(97, 98, 100, 120)"


SIDEBAR_TEXT_COLOR = "black"
SIDEBAR_SELECTED_TEXT_COLOR = "white"


class AppShell(QWidget):
    def __init__(self, on_page_change):
        super().__init__()
        self.on_page_change = on_page_change

        #---------- Main horizontal layout----------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------- Sidebar ----------
        self.sidebar = QListWidget()
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {SIDEBAR_BG_COLOR};
                border: none;
                padding-top: 8px;
                outline: 0;
            }}

            QListWidget::item {{
                padding: 10px 12px;
                margin: 6px 8px;
                border-radius: 6px;
                color: {SIDEBAR_TEXT_COLOR};
            }}

            QListWidget::item:selected {{
                background-color: {SIDEBAR_ITEM_SELECTED_BG};
                color: {SIDEBAR_SELECTED_TEXT_COLOR};
            }}

            QListWidget::item:selected:!active {{
                background-color: {SIDEBAR_ITEM_SELECTED_BG};
                color: {SIDEBAR_SELECTED_TEXT_COLOR};
            }}

            QListWidget::item:hover {{
                background-color: {SIDEBAR_ITEM_HOVER_BG};
            }}
            """)

        self.sidebar.addItems([
            "Dashboard",
            "Scan",
            "Adding Files",
            "Resume",
            "Portfolio",
            "Settings",
        ])
        self.sidebar.setFixedWidth(180)
        self.sidebar.currentTextChanged.connect(self.change_page)
        main_layout.addWidget(self.sidebar)

        # ---------- Right area  ----------
        right_area = QWidget()
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header
        self.header = QLabel("Dashboard")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFixedHeight(50)
        self.header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 12px;
                background-color: #002145;
                color: white;
            }
        """)
        right_layout.addWidget(self.header)

        # Content area
        self.content = QLabel("Dashboard content goes here")
        self.content.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.content, 1)  # stretch=1 to fill space

        main_layout.addWidget(right_area, 1)  # right_area stretches

        # Set first page
        self.sidebar.setCurrentRow(0)

    def change_page(self, page_name: str):
        self.header.setText(page_name)
        self.content.setText(f"{page_name} content goes here")

        if self.on_page_change:
            self.on_page_change(page_name)
