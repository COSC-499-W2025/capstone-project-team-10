from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from pathlib import Path
from datetime import datetime
import src.log.log as log
from src.gui.gui_utils.gui_styles import BUTTON_STYLE

class DashboardPage(QWidget):
    log_clicked = pyqtSignal(object)
    
    def __init__(self, log_file=None):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        self.log_file = log_file or Path(log.current_log_file)
        self.log_dir = self.log_file.parent
        self.log_files = {}
        self.table = None
        self._tab_widget = None
        self._favourites_placeholder = None
        self.init_ui()
        self.load_log_files()
        self.update_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #d0d0d0;
                color: #666;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: black;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
        
        recent_widget = self.create_recent_tab()
        
        self._favourites_placeholder = QWidget()
        self._favourites_placeholder.setStyleSheet("background-color: white;")
        placeholder_layout = QVBoxLayout(self._favourites_placeholder)
        placeholder_layout.addWidget(
            QLabel("Loading favourites…", alignment=Qt.AlignCenter)
        )

        self._tab_widget.addTab(recent_widget, "Recent") # index 0
        self._tab_widget.addTab(self._favourites_placeholder, "Favourite") # index 1
        
        layout.addWidget(self._tab_widget)

    def set_favourites_widget(self, favourites_widget: QWidget):
        self._tab_widget.removeTab(1)
        self._tab_widget.addTab(favourites_widget, "Favourite")

    def create_recent_tab(self):
        recent_widget = QWidget()
        recent_layout = QVBoxLayout(recent_widget)
        recent_layout.setContentsMargins(20, 20, 20, 20)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Size", "Date Created", ""])
        
        self.table.cellDoubleClicked.connect(self.on_cell_clicked)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e0e0e0;
                border: none;
                color: black;
            }
            QHeaderView::section {
                background-color: white;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: normal;
                color: #666;
            }
            QTableWidget::item {
                padding: 8px 8px 8px 0px;
                border-bottom: 1px solid #e0e0e0;
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #002145;
                color: white;
            }
        """)
        
        self.table.viewport().setCursor(Qt.PointingHandCursor)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 90)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        recent_layout.addWidget(self.table)
        
        bottom_label = QLabel(f"All logs are located at {self.log_dir}")
        bottom_label.setStyleSheet("color: #999; font-size: 12px;")
        bottom_label.setAlignment(Qt.AlignCenter)
        recent_layout.addWidget(bottom_label)
        
        return recent_widget

    def on_cell_clicked(self, row, column):
        file_name_item = self.table.item(row, 0)
        if file_name_item:
            file_name = file_name_item.text()
            if file_name in self.log_files:
                log_path = self.log_files[file_name]['path']
                self.log_clicked.emit(log_path)
    
    def load_log_files(self):
        self.log_files.clear()
        if not self.log_dir.exists():
            return
        
        for log_path in self.log_dir.glob("*.log"):
            file_stat = log_path.stat()
            self.log_files[log_path.name] = {
                'path': log_path,
                'name': log_path.name,
                'size': self.format_file_size(file_stat.st_size),
                'created': datetime.fromtimestamp(file_stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            }
    
    def format_file_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def update_table(self):
        if self.table is None:
            return
        
        self.table.setRowCount(0)
        
        sorted_logs = sorted(
            self.log_files.items(), 
            key=lambda x: x[1]['created'], 
            reverse=True
        )
        
        for idx, (file_name, log_info) in enumerate(sorted_logs):
            self.table.insertRow(idx)
            self.table.setItem(idx, 0, QTableWidgetItem(log_info['name']))
            self.table.setItem(idx, 1, QTableWidgetItem(log_info['size']))
            self.table.setItem(idx, 2, QTableWidgetItem(log_info['created']))

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet(BUTTON_STYLE)
            delete_btn.clicked.connect(lambda _, p=log_info['path']: self.delete_log(p))
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(6, 4, 6, 4)
            btn_layout.addWidget(delete_btn)
            self.table.setCellWidget(idx, 3, btn_container)
    
    def delete_log(self, log_path):
        reply = QMessageBox.question(
            self, "Delete Log",
            f"Delete {log_path.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                log_path.unlink()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete log: {e}")
        self.refresh_log()

    def refresh_log(self):
        self.load_log_files()
        self.update_table()