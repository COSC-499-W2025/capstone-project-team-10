import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from src.gui.gui_scan_filtering import FilterDialog
from src.gui.gui_scan_manager import ScanManager
import src.gui.gui_utils.gui_styles as styles


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

        # Main Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(0) # We will manually control spacing between specific elements

        # Top Buffer
        self.layout.addSpacing(60)

        # Title (Top Center)
        self.title_label = QtWidgets.QLabel("Scan!")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        self.layout.addWidget(self.title_label)
        
        self.layout.addSpacing(30) # Gap below title

        # 1. Directory Group (Centered, text below button)
        self.browse_button = QtWidgets.QPushButton("Choose Directory", self)
        self.browse_button.setFixedSize(160, 40)
        self.browse_button.setStyleSheet(styles.BUTTON_STYLE)
        self.browse_button.clicked.connect(self.browse_files)
        
        self.directory_label = QtWidgets.QLabel("No directory selected")
        self.directory_label.setAlignment(QtCore.Qt.AlignCenter)
        self.directory_label.setStyleSheet("font-size: 13px; color: #555;")
        
        self.layout.addWidget(self.browse_button, alignment=QtCore.Qt.AlignCenter)
        self.layout.addSpacing(8) # Small gap between button and its label
        self.layout.addWidget(self.directory_label, alignment=QtCore.Qt.AlignCenter)

        self.layout.addSpacing(30) # Gap between Directory section and Filters section

        # 2. Filters Group (Centered, text below button)
        self.filter_button = QtWidgets.QPushButton("Choose Filters", self)
        self.filter_button.setFixedSize(160, 40)
        self.filter_button.setStyleSheet(styles.BUTTON_STYLE)
        self.filter_button.clicked.connect(self.open_filter_dialog)
        
        self.filter_summary = QtWidgets.QLabel("No filters applied")
        self.filter_summary.setAlignment(QtCore.Qt.AlignCenter) # Center the multi-line text
        self.filter_summary.setStyleSheet("font-size: 13px; color: #333;")
        
        self.layout.addWidget(self.filter_button, alignment=QtCore.Qt.AlignCenter)
        self.layout.addSpacing(8) # Small gap between button and its label
        self.layout.addWidget(self.filter_summary, alignment=QtCore.Qt.AlignCenter)

        # Add a spring to push the "Start Scan" button to the bottom
        self.layout.addStretch()

        # 3. Start Scan Button (Bottom Middle)
        self.scan_button = QtWidgets.QPushButton("Start Scan", self)
        self.scan_button.setFixedSize(200, 45)
        self.scan_button.setStyleSheet(styles.BUTTON_STYLE)
        self.scan_button.clicked.connect(self.start_scan)
        
        self.layout.addWidget(self.scan_button, alignment=QtCore.Qt.AlignCenter)
        
        # Bottom Buffer
        self.layout.addSpacing(100) 

    def browse_files(self):
        chooser = QtWidgets.QMessageBox(self)
        chooser.setWindowTitle("Select Input")
        chooser.setText("What would you like to scan?")
        folder_btn = chooser.addButton("Folder", QtWidgets.QMessageBox.ActionRole)
        zip_btn = chooser.addButton("Zip file (.zip)", QtWidgets.QMessageBox.ActionRole)
        chooser.addButton(QtWidgets.QMessageBox.Cancel)
        chooser.exec_()

        if chooser.clickedButton() is folder_btn:
            selected_path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select a directory to scan",
                "",
                QtWidgets.QFileDialog.ShowDirsOnly,
            )
            if not selected_path:
                return

        elif chooser.clickedButton() is zip_btn:
            selected_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Select a zip file to scan",
                "",
                "Zip files (*.zip)",
            )
            if not selected_path:
                return

        else:
            return

        self.selected_directory = selected_path
        self.directory_label.setText(f"{self.selected_directory}")

    def open_filter_dialog(self):
        filter_dialog = FilterDialog(self)
        if filter_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.current_filters = filter_dialog.get_filters()
            self.display_filters(self.current_filters)

    def start_scan(self):
        if not self.selected_directory:
            QtWidgets.QMessageBox.warning(
                self, "No Input", "Please select a directory or .zip file first."
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

        scan_params = {
            "directory": self.selected_directory,
            "filters": self.current_filters,
        }
        self.scan_started.emit(scan_params)

    def _on_scan_finished(self, result: int):
        self.scan_finished.emit(result)

    def _on_scan_failed(self, message: str):
        QtWidgets.QMessageBox.critical(self, "Scan Failed", message)

    def display_filters(self, filters):
        summary = ""

        # File types
        if filters["file_types"]:
            summary += f"• File Types: {', '.join(filters['file_types'])}\n"

        # Excluded paths
        if filters["excluded_paths"]:
            summary += "• Excluded Paths:\n"
            for path in filters["excluded_paths"]:
                summary += f"    - {path}\n"

        # Time bounds
        if filters["time_lower_bound"] or filters["time_upper_bound"]:
            lower = filters["time_lower_bound"].strftime("%Y-%m-%d") if filters["time_lower_bound"] else "None"
            upper = filters["time_upper_bound"].strftime("%Y-%m-%d") if filters["time_upper_bound"] else "None"
            summary += f"• Time Bounds: {lower} to {upper}\n"

        if filters.get('clean', False):
            summary += "• New Log: Yes\n"
            
        if not summary:
            summary = "No filters applied"

        self.filter_summary.setText(summary.strip())
        self.filter_summary.setVisible(True)