from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.gui_dashboard.gui_dashboard_container import DashboardContainer
from src.gui.gui_items_page.gui_items_page import ItemsPage
from src.gui.gui_portfolio_page import PortfolioPage
from src.gui.gui_resume_page import ResumePage
from src.gui.gui_scan_page import ScanPage
from src.gui.gui_scan_results import ScanResultsPage
from src.gui.gui_settings_page.gui_settings_page import SettingsPage

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
        # Now header + sidebar list
        left_area = QWidget()
        left_layout = QVBoxLayout(left_area)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.header = QLabel("")  # keep blank
        self.header.setFixedHeight(70)
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet(f"""
            QLabel {{
                background-color: {HEADER_BG_COLOR};
                color: white;
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        left_layout.addWidget(self.header)

        # Sidebar list
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
            "Items",
            "Resume/Portfolio",
            "Settings",
        ]
        self.sidebar.addItems(self.sidebar_items)

        self.sidebar.setFixedWidth(220)
        self.sidebar.currentTextChanged.connect(self.change_page)

        left_layout.addWidget(self.sidebar, 1)

        # Add left area to main layout
        main_layout.addWidget(left_area)

        # ---------- Right area ----------
        right_area = QWidget()
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # ---------- Content stack ----------
        self.content_stack = QStackedWidget()
        right_layout.addWidget(self.content_stack, 1)

        # ---------- Pages ----------
        self.page_dashboard = DashboardContainer()

        self.page_resume = ResumePage()
        # self.page_portfolio = PortfolioPage()

        self.page_scan = ScanPage()
        self.page_scan_results = ScanResultsPage()

        self.page_items = ItemsPage()

        self.page_settings = SettingsPage()

        # Add pages to stack (order matters)
        self.content_stack.addWidget(self.page_dashboard)  # index 0
        self.content_stack.addWidget(self.page_scan)  # index 1
        self.content_stack.addWidget(self.page_items)  # index 2
        self.content_stack.addWidget(self.page_resume)  # index 3
        # self.content_stack.addWidget(self.page_portfolio)  # index 4
        self.content_stack.addWidget(self.page_settings)  # index 5
        self.content_stack.addWidget(self.page_scan_results)  # index 6

        # Connect signals AFTER all pages are created
        self.page_scan.scan_started.connect(self.page_scan_results.on_scan_started)
        self.page_scan.scan_started.connect(self.on_scan_started)
        self.page_scan.scan_finished.connect(self.page_scan_results.on_scan_finished)
        self.page_scan.scan_finished.connect(self.page_resume.refresh_from_scan)
        self.page_scan.scan_output.connect(self.page_scan_results.append_output)
        self.page_scan_results.back_to_scan.connect(self.return_to_scan)
        self.page_scan.scan_finished.connect(
            lambda result: self.page_scan_results.back_button.setEnabled(True)
        )

        # Add right area to main layout
        main_layout.addWidget(right_area, 1)

        # Set first page
        self.sidebar.setCurrentRow(0)

    def change_page(self, page_name: str):

        # Switch stack page
        if page_name == "Dashboard":
            self.content_stack.setCurrentWidget(self.page_dashboard)

        elif page_name == "Scan":
            self.content_stack.setCurrentWidget(self.page_scan)

        elif page_name == "Items":
            self.content_stack.setCurrentWidget(self.page_items)

        elif page_name == "Resume/Portfolio":
            self.content_stack.setCurrentWidget(self.page_resume)

        # elif page_name == "Portfolio":
        #     self.content_stack.setCurrentWidget(self.page_portfolio)

        elif page_name == "Settings":
            self.content_stack.setCurrentWidget(self.page_settings)

        elif page_name == "scan_results":
            self.content_stack.setCurrentWidget(self.page_scan_results)
            # Don't update sidebar for this hidden page

        if self.on_page_change:
            self.on_page_change(page_name)

    def on_scan_started(self, scan_params):
        """Switch to results page and start animation"""
        self.sidebar.blockSignals(True)
        self.change_page("scan_results")
        self.page_scan_results.start_scan_animation()
        self.sidebar.blockSignals(False)

    def return_to_scan(self):
        """Return from scan results to scan page"""
        self.sidebar.setCurrentRow(1)  # Set to "Scan" item
        self.change_page("Scan")

    def closeEvent(self, event):
        self.page_scan.scan_manager.cleanup()
        event.accept()
