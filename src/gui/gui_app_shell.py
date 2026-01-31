from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QStackedWidget
)
from PyQt5.QtCore import Qt

from src.gui.gui_resume_page import ResumePage  
from src.gui.gui_portfolio_page import PortfolioPage


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

        # ---------- Main horizontal layout ----------
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

        self.sidebar_items = [
            "Dashboard",
            "Scan",
            "Adding Files",
            "Resume",
            "Portfolio",
            "Settings",
        ]
        self.sidebar.addItems(self.sidebar_items)

        self.sidebar.setFixedWidth(180)
        self.sidebar.currentTextChanged.connect(self.change_page)
        main_layout.addWidget(self.sidebar)

        # ---------- Right area ----------
        right_area = QWidget()
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header
        self.header = QLabel("Dashboard")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFixedHeight(50)
        self.header.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                padding: 12px;
                background-color: {HEADER_BG_COLOR};
                color: white;
            }}
        """)
        right_layout.addWidget(self.header)

        # ---------- Content stack ----------
        self.content_stack = QStackedWidget()
        right_layout.addWidget(self.content_stack, 1)

        # ---------- Pages ----------
        self.page_dashboard = QLabel("Dashboard content goes here")
        self.page_dashboard.setAlignment(Qt.AlignCenter)

        self.page_scan = QLabel("Scan content goes here")
        self.page_scan.setAlignment(Qt.AlignCenter)

        self.page_add_files = QLabel("Adding Files content goes here")
        self.page_add_files.setAlignment(Qt.AlignCenter)

        self.page_resume = ResumePage()

        # self.page_portfolio = QLabel("Portfolio content goes here")
        # self.page_portfolio.setAlignment(Qt.AlignCenter)
        self.page_portfolio = PortfolioPage()

        self.page_settings = QLabel("Settings content goes here")
        self.page_settings.setAlignment(Qt.AlignCenter)

        # Add pages to stack (order matters)
        self.content_stack.addWidget(self.page_dashboard)   # index 0
        self.content_stack.addWidget(self.page_scan)        # index 1
        self.content_stack.addWidget(self.page_add_files)   # index 2
        self.content_stack.addWidget(self.page_resume)      # index 3
        self.content_stack.addWidget(self.page_portfolio)   # index 4
        self.content_stack.addWidget(self.page_settings)    # index 5

        main_layout.addWidget(right_area, 1)

        # Set first page
        self.sidebar.setCurrentRow(0)

    def change_page(self, page_name: str):
        self.header.setText(page_name)

        # Switch stack page
        if page_name == "Dashboard":
            self.content_stack.setCurrentWidget(self.page_dashboard)

        elif page_name == "Scan":
            self.content_stack.setCurrentWidget(self.page_scan)

        elif page_name == "Adding Files":
            self.content_stack.setCurrentWidget(self.page_add_files)

        elif page_name == "Resume":
            self.content_stack.setCurrentWidget(self.page_resume)

        elif page_name == "Portfolio":
            self.content_stack.setCurrentWidget(self.page_portfolio)

        elif page_name == "Settings":
            self.content_stack.setCurrentWidget(self.page_settings)

        if self.on_page_change:
            self.on_page_change(page_name)
