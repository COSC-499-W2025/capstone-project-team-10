from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
import sys

def run_gui():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("PyQt GUI App")
    layout = QVBoxLayout()
    label = QLabel("Hello from PyQt GUI!")
    layout.addWidget(label)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())