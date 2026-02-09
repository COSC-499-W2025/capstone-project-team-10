from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from src.gui.gui_dashboard.gui_dashboard_page import DashboardPage
from src.gui.gui_dashboard.gui_log_details_page import LogDetailsPage

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
        
        self.dashboard_page = DashboardPage(log_file)
        self.log_details_page = LogDetailsPage()
        
        # Adding stacked pages to the dashboard container
        self.stacked_widget.addWidget(self.dashboard_page)  # Index 0
        self.stacked_widget.addWidget(self.log_details_page)  # Index 1
        
        # Connect signals to transfer specific logs
        self.dashboard_page.log_clicked.connect(self.show_log_details)
        self.log_details_page.back_clicked.connect(self.show_dashboard)
        
        layout.addWidget(self.stacked_widget)
        
        self.stacked_widget.setCurrentIndex(0)
    
    def show_log_details(self, log_path):
        self.log_details_page.set_log_path(log_path)
        self.stacked_widget.setCurrentIndex(1)
    
    def show_dashboard(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def refresh_log(self):
        self.dashboard_page.refresh_log()