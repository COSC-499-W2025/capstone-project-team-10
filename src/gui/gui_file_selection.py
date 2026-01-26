from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent

class DropButton(QPushButton):
    """Button that also accepts drag and drop."""
    
    # Style for regular button behaviours eg. click and hover
    SELECT_STYLE = """
        QPushButton {
            border: 2px dashed #888;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #dbdbdb;
        }
    """
    
    # Style for file drag and drop behaviour
    DRAG_STYLE = """
        QPushButton {
            border: 2px dashed #888;
            border-radius: 8px;
            background-color: #c0d8f0;
        }
    """
    
    def __init__(self, parent: "FileSelectionWidget"):
        super().__init__(parent)
        self.parent_widget = parent
        self.setText("Click to select or drag a folder here")
        self.setAcceptDrops(True)
        self.setFixedSize(500, 50)
        self.setStyleSheet(self.SELECT_STYLE)
        self.clicked.connect(self.parent_widget.open_file_dialog)

    def dragEnterEvent(self, event: QDragEnterEvent | None) -> None:  # type: ignore[override]
        if event:
            mime_data = event.mimeData()
            if mime_data and mime_data.hasUrls():
                event.acceptProposedAction()
                self.setStyleSheet(self.DRAG_STYLE)

    def dragLeaveEvent(self, event: QDragLeaveEvent | None) -> None:  # type: ignore[override]
        if event:
            self.setStyleSheet(self.SELECT_STYLE)

    def dropEvent(self, event: QDropEvent | None) -> None:  # type: ignore[override]
        if event:
            mime_data = event.mimeData()
            if mime_data and mime_data.hasUrls():
                filepath = mime_data.urls()[0].toLocalFile()
                self.parent_widget.set_selected_path(filepath)
                self.setStyleSheet(self.SELECT_STYLE)

class FileSelectionWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.selected_file: str | None = None

        layout = QVBoxLayout(self)

        layout.addStretch(1)

        # Select/Drop button
        self.drop_button = DropButton(self)
        layout.addWidget(self.drop_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Filepath label
        self.label = QLabel("No folder selected")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)

    def open_file_dialog(self) -> None:
        filepath = QFileDialog.getExistingDirectory(self, "Select Folder")
        if filepath:
            self.set_selected_path(filepath)

    def set_selected_path(self, filepath: str) -> None:
        """Set the selected path and update the label."""
        self.selected_file = filepath
        self.label.setText(filepath)