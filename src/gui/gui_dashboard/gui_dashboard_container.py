from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from src.gui.gui_dashboard.gui_dashboard_page import DashboardPage
from src.gui.gui_dashboard.gui_log_details_page import LogDetailsPage
from src.gui.gui_dashboard.gui_favourites_page import FavouritesPage


class DashboardContainer(QWidget):

    def __init__(self, log_file=None):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        self.init_ui(log_file)

    def init_ui(self, log_file):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        self._came_from_favourites = False  # tracks back-navigation context

        # pages
        self.dashboard_page = DashboardPage(log_file)   # index 0
        self.log_details_page = LogDetailsPage()         # index 1
        self.favourites_page = FavouritesPage()          # index 2

        self.dashboard_page.set_favourites_widget(self.favourites_page)

        self.stacked_widget.addWidget(self.dashboard_page)    # 0
        self.stacked_widget.addWidget(self.log_details_page)  # 1

        # signals
        # Recent tab: open a log, show LogDetailsPage
        self.dashboard_page.log_clicked.connect(self.show_log_details)

        # LogDetailsPage "Back" button, always returns to dashboard
        self.log_details_page.back_clicked.connect(self.show_dashboard)

        # Return to the project list or directly to the favourites tab
        self.log_details_page.project_files_page.back_clicked.connect(
            self._on_project_files_back
        )

        # Whenever a favourite is toggled, refresh the FavouritesPage tab
        self.log_details_page.favourites_changed.connect(
            self.favourites_page.refresh
        )

        # FavouritesPage: double-click a project, navigate directly to it
        self.favourites_page.project_clicked.connect(
            self._open_project_from_favourites
        )

        layout.addWidget(self.stacked_widget)
        self.stacked_widget.setCurrentIndex(0)

    def show_log_details(self, log_path):
        self._came_from_favourites = False
        self.log_details_page.set_log_path(log_path)
        self.stacked_widget.setCurrentIndex(1)

    def show_dashboard(self):
        self._came_from_favourites = False
        self.stacked_widget.setCurrentIndex(0)

    def _on_project_files_back(self):
        if self._came_from_favourites:
            self._came_from_favourites = False
            self.log_details_page.stack.setCurrentIndex(0)
            self.stacked_widget.setCurrentIndex(0)
            self.dashboard_page._tab_widget.setCurrentIndex(1)
        else:
            self.log_details_page.stack.setCurrentIndex(0)

    def _open_project_from_favourites(self, project_id: str, log_path):
        import src.log.log as log_module
        self._came_from_favourites = True
        self.log_details_page.set_log_path(log_path)
        files = log_module.get_project(project_id)
        self.log_details_page.project_files_page.load_project_files(project_id, files)
        self.log_details_page.stack.setCurrentIndex(1)
        self.stacked_widget.setCurrentIndex(1)

    def refresh_log(self):
        self.dashboard_page.refresh_log()