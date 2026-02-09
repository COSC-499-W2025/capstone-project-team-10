import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

class ScanResultsPage(QtWidgets.QWidget):

    back_to_scan = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ScanResultsPage, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(20)

        layout.addStretch()

        # Status label for animation
        self.status_label = QtWidgets.QLabel("Scanning")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #007AFF; }")
        layout.addWidget(self.progress_bar)

        # Files being scanned list
        self.file_list = QtWidgets.QListWidget()
        layout.addWidget(self.file_list)

        layout.addStretch()

        # Back button
        self.back_button = QtWidgets.QPushButton("Back to Scan")
        self.back_button.setFixedSize(200, 50)
        self.back_button.clicked.connect(self.back_to_scan.emit)
        layout.addWidget(self.back_button, alignment=QtCore.Qt.AlignCenter)

        # Animation timer (single stage)
        self.dot_count = 0
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout.connect(self.update_animation)

    def start_scan_animation(self):
        """
          Start the scan animation sequence
        """
        self.dot_count = 0
        self.file_list.clear()
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.status_label.setText("Scanning")
        self.animation_timer.start(500)

    def update_animation(self):
        """
          Update the animation dots
        """
        dots = "." * (self.dot_count % 4)
        self.status_label.setText(f"Scanning{dots}")
        self.dot_count += 1

    def append_output(self, text: str):
        for line in text.splitlines():
            self.file_list.addItem(line)
        self.file_list.scrollToBottom()

    def on_scan_started(self):
        self.back_button.setEnabled(False)

    def on_scan_finished(self, result: int):
        self.animation_timer.stop()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setTextVisible(False)

        if result == 0:
            self.status_label.setText("Scan Complete (no new files detected)")
            self.file_list.addItem("No new files were scanned (all files were skipped by the log).")
        else:
            self.status_label.setText(f"Scan Complete ({result} files)")