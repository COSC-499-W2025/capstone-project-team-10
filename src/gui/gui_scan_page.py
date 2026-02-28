import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from src.gui.gui_scan_filtering import FilterDialog
from src.gui.gui_scan_manager import ScanManager


class ScanPage(QtWidgets.QWidget):
    scan_started = QtCore.pyqtSignal(dict)
    scan_finished = QtCore.pyqtSignal(int)
    scan_output = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(ScanPage, self).__init__(parent)

        self.scan_manager = ScanManager()
        self.selected_directory = None
        self.current_filters = None

        self.scan_manager.scan_finished.connect(self._on_scan_finished)
        self.scan_manager.scan_failed.connect(self._on_scan_failed)
        self.scan_manager.scan_output.connect(self.scan_output.emit)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.setSpacing(20)

        self.layout.addStretch()

        # Title
        self.title_label = QtWidgets.QLabel("Scan!")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Directory label
        self.directory_label = QtWidgets.QLabel("No directory selected")
        self.directory_label.setAlignment(QtCore.Qt.AlignCenter)
        self.directory_label.setStyleSheet("font-size: 12px; color: gray;")
        self.layout.addWidget(self.directory_label)

        # Button container for centering
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Button 1 - Choose directory
        self.browse_button = QtWidgets.QPushButton("Choose Directory", self)
        self.browse_button.setFixedSize(200, 50)
        self.browse_button.clicked.connect(self.browse_files)
        button_layout.addWidget(self.browse_button, alignment=QtCore.Qt.AlignCenter)

        # Button 2 - Choose filters
        self.filter_button = QtWidgets.QPushButton("Choose Filters", self)
        self.filter_button.setFixedSize(200, 50)
        self.filter_button.clicked.connect(self.open_filter_dialog)
        button_layout.addWidget(self.filter_button, alignment=QtCore.Qt.AlignCenter)

        # Button 3 - Start scan
        self.scan_button = QtWidgets.QPushButton("Start Scan", self)
        self.scan_button.setFixedSize(200, 50)
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button, alignment=QtCore.Qt.AlignCenter)

        self.layout.addLayout(button_layout)
        self.layout.addStretch()

        # Filter summary section (initially hidden)
        self.filter_summary = QtWidgets.QLabel()
        self.filter_summary.setAlignment(QtCore.Qt.AlignCenter)
        self.filter_summary.setStyleSheet("font-size: 10px; color: blue;")
        self.filter_summary.setVisible(False)
        self.layout.addWidget(self.filter_summary)

    def browse_files(self):
        file_dialog = QtWidgets.QFileDialog(
            self, "Select a directory or zip file to scan"
        )
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        file_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, False)
        file_dialog.setNameFilter("Zip files (*.zip);;All files (*)")
        selected_path = ""
        if file_dialog.exec_():
            selected_path = file_dialog.selectedFiles()[0]

        if selected_path:
            self.selected_directory = selected_path
            # Display on GUI
            self.directory_label.setText(f"Directory: {selected_path}")

    def open_filter_dialog(self):
        filter_dialog = FilterDialog(self)
        if filter_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.current_filters = filter_dialog.get_filters()
            self.display_filters(self.current_filters)

    def start_scan(self):
        if not self.selected_directory:
            QtWidgets.QMessageBox.warning(
                self, "No Directory", "Please select a directory first."
            )
            return

        if self.current_filters is None:
            QtWidgets.QMessageBox.warning(
                self, "No Filters", "Please choose filters first."
            )
            return

        started = self.scan_manager.scan_async(
            directory_path=self.selected_directory, filters=self.current_filters
        )
        if not started:
            QtWidgets.QMessageBox.information(
                self, "Scan Running", "A scan is already running."
            )
            return

        # Emit immediately so results page can show animation
        scan_params = {
            "directory": self.selected_directory,
            "filters": self.current_filters,
        }
        self.scan_started.emit(scan_params)

    def _on_scan_finished(self, result: int):
        self.scan_finished.emit(result)

    def _on_scan_failed(self, message: str):
        QtWidgets.QMessageBox.critical(self, "Scan Failed", message)

    def display_filters(self, filters):  # Can be removed later
        summary = "Applied Filters:\n"

        # File types
        if filters["file_types"]:
            summary += f"File Types: {', '.join(filters['file_types'])}\n"
        else:
            summary += "File Types: None\n"

        # Excluded paths
        if filters["excluded_paths"]:
            summary += f"Excluded Paths: {len(filters['excluded_paths'])} path(s)\n"
        else:
            summary += "Excluded Paths: None\n"

        # Time bounds
        if filters["time_lower_bound"] or filters["time_upper_bound"]:
            lower = (
                filters["time_lower_bound"].strftime("%Y-%m-%d %H:%M:%S")
                if filters["time_lower_bound"]
                else "None"
            )
            upper = (
                filters["time_upper_bound"].strftime("%Y-%m-%d %H:%M:%S")
                if filters["time_upper_bound"]
                else "None"
            )
            summary += f"Time Bounds: {lower} to {upper}"
        else:
            summary += "Time Bounds: None"

        self.filter_summary.setText(summary)
        self.filter_summary.setVisible(True)
