from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import Qt

class DropBox(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setText("Drag and drop folder here")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px dashed; padding: 20px;")
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event): # type: ignore
        if event.mimeData().hasUrls():
            event.accept()
    
    def dropEvent(self, event): # type: ignore
        filepath = event.mimeData().urls()[0].toLocalFile()
        self.parent_widget.selected_file = filepath # type: ignore
        self.parent_widget.label.setText(filepath) # type: ignore

class FileSelectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("No folder selected")
        layout.addWidget(self.label)
        
        btn = QPushButton("Select Folder")
        btn.clicked.connect(self.open_file_dialog)
        layout.addWidget(btn)
        
        self.dropbox = DropBox(self)
        layout.addWidget(self.dropbox)
    
    def open_file_dialog(self):
        filepath = QFileDialog.getExistingDirectory(self, "Select Folder")
        if filepath:
            self.selected_file = filepath
            self.label.setText(filepath)