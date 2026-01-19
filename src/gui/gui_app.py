from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget
import sys
from pathlib import Path
import shutil
import src.gui.gui_eula_mgr.gui_perms_prompt as perms_prompt
import src.param.param as param

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Team 10 Capstone")
        self.setMinimumSize(400, 300)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_content = QWidget()
        self.stack.addWidget(self.main_content)

        self.eula_prompt = None 

    def show_eula_prompt(self, eula_folder, persisted_eula):
        # Remove old EULA prompt if it exists
        if self.eula_prompt is not None:
            self.stack.removeWidget(self.eula_prompt)
            self.eula_prompt.deleteLater()
            self.eula_prompt = None

        # Create EULA prompt, passing a callback to restore the main content
        self.eula_prompt = perms_prompt.PermsPromptWindow(
            persisted_eula,
            on_accept=self.restore_main_content
        )
        self.stack.addWidget(self.eula_prompt)
        self.stack.setCurrentWidget(self.eula_prompt)

    def restore_main_content(self):
        self.stack.setCurrentWidget(self.main_content)
        if self.eula_prompt is not None:
            self.stack.removeWidget(self.eula_prompt)
            self.eula_prompt.deleteLater()
            self.eula_prompt = None

def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    eula_folder = Path(param.program_file_path) / "eula"
    persisted_eula = eula_folder / f"eula_{param.eula_date}.done"
    if not persisted_eula.is_file():
        if eula_folder.is_dir():
            shutil.rmtree(eula_folder)
        window.show_eula_prompt(eula_folder, persisted_eula)
    #Other Content Loading ->
    
    window.show()
    sys.exit(app.exec_())
