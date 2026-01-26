from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget ,QStackedWidget
)
from PyQt5.QtCore import Qt
from src.gui.gui_file_selection import FileSelectionWidget

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

        self.page_names = [
            "Dashboard",
            "Scan",
            "Adding Files",
            "Resume",
            "Portfolio",
            "Settings",
        ]
        self.sidebar.addItems(self.page_names)
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

        self.content_stack = QStackedWidget()
        right_layout.addWidget(self.content_stack, 1)

        self.pages = {}
        
        # Create each page for the stack
        for name in self.page_names:
            self.pages[name] = self._create_page(name)  # Called once per page
            self.content_stack.addWidget(self.pages[name])

        main_layout.addWidget(right_area, 1)  # right_area stretches

        # Set first page
        self.sidebar.setCurrentRow(0)

    def _create_page(self, page_name: str) -> QWidget | None:
        "Function to create a widget for each page."
        match page_name:
            case "Dashboard":
                # TODO: Add DashboardWidget
                return self._create_placeholder(page_name)

            case "Scan":
                return FileSelectionWidget()

            case "Adding Files":
                # TODO: Add AddingFilesWidget
                return self._create_placeholder(page_name)

            case "Resume":
                # TODO: Add ResumeWidget
                return self._create_placeholder(page_name)

            case "Portfolio":
                # TODO: Add PortfolioWidget
                return self._create_placeholder(page_name)

            case "Settings":
                # TODO: Add SettingsWidget
                return self._create_placeholder(page_name)

    def _create_placeholder(self, page_name: str) -> QWidget:
        """Create a placeholder label for pages not yet implemented."""
        label = QLabel(f"{page_name} content goes here")
        label.setAlignment(Qt.AlignCenter)
        return label

    def change_page(self, page_name: str):
        self.header.setText(page_name)
        self.content_stack.setCurrentWidget(self.pages[page_name])

        if self.on_page_change:
            self.on_page_change(page_name)

    def get_page(self, page_name: str) -> QWidget | None:
        """Access a specific page widget by name."""
        return self.pages.get(page_name)