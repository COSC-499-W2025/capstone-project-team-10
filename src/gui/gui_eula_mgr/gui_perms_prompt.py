from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QTextEdit
import sys
from pathlib import Path
import shutil
import os

class PermsPromptWindow(QWidget):
    def __init__(self, eula_accept: Path, on_accept=None):
        super().__init__()
        self.eula_accept = eula_accept
        self.on_accept = on_accept
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Load EULA.txt
        eula_path = Path(os.path.dirname(__file__)) / "EULA.txt"
        if eula_path.exists():
            with open(eula_path, "r", encoding="utf-8") as f:
                eula_text = f.read()
        else:
            eula_text = "EULA file not found."

        self.eula_display = QTextEdit()
        self.eula_display.setReadOnly(True)
        self.eula_display.setPlainText(eula_text)
        self.layout.addWidget(self.eula_display)

        self.label = QLabel("Do you accept the End User License Agreement?")
        self.layout.addWidget(self.label)

        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")
        self.layout.addWidget(self.yes_button)
        self.layout.addWidget(self.no_button)

        self.yes_button.clicked.connect(self.handleYes)
        self.no_button.clicked.connect(self.handleNo)

    def handleYes(self):
        self.label.setText("Thank you for accepting the EULA!")
        self.eula_accept.parent.mkdir(parents=True, exist_ok=True)
        self.eula_accept.touch(exist_ok=True)
        if self.on_accept:
            self.on_accept()

    def handleNo(self):
        sys.exit(0)
