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
        
        # Animation timer
        self.dot_count = 0
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        # Stage timer (for switching between Scanning and Analysis)
        self.stage_timer = QtCore.QTimer()
        self.stage_timer.setSingleShot(True)
        self.stage_timer.timeout.connect(self.switch_stage)
        
        self.current_stage = "scanning"  # "scanning" or "analysis"
    
    def start_scan_animation(self):
        """
          Start the scan animation sequence
        """
        self.current_stage = "scanning"
        self.dot_count = 0
        self.file_list.clear()
        self.progress_bar.setMaximum(0)  # Indeterminate
        
        # Start scanning animation for 2 seconds
        self.animation_timer.start(500)
        self.stage_timer.start(2000)  # Switch to analysis after 2 seconds
    
    def update_animation(self):
        """
          Update the animation dots
        """
        dots = "." * (self.dot_count % 4)
        
        if self.current_stage == "scanning":
            self.status_label.setText(f"Scanning{dots}")
        else:
            self.status_label.setText(f"Analyzing{dots}")
        
        self.dot_count += 1
    
    def switch_stage(self):
        """
          Switch from Scanning to Analysis or finish
        """
        if self.current_stage == "scanning":
            self.current_stage = "analysis"
            self.dot_count = 0
            self.stage_timer.start(2000)
        else:
            # Scan complete
            self.animation_timer.stop()
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(100)
            self.progress_bar.setTextVisible(False)
            self.status_label.setText("Scan Complete")