from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget
import sys
from pathlib import Path
import shutil
from src.gui.gui_app_shell import AppShell
import src.gui.gui_eula_mgr.gui_perms_prompt as perms_prompt
import src.gui.gui_file_selection as file_selection
import src.param.param as param

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Team 10 Capstone")
        self.setMinimumSize(900, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # self.main_content = QWidget()
        # self.stack.addWidget(self.main_content)
        # Shared app state (FAS results, etc.)
        self.app_state = {}

        # Main application UI
        self.app_shell = AppShell(on_page_change=self.on_page_change)
        self.stack.addWidget(self.app_shell)

        self.eula_prompt = None 
        self.file_selector = None


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

    def show_file_selector(self):
        if self.file_selector is not None:
            self.stack.removeWidget(self.file_selector)
            self.file_selector.deleteLater()
            self.file_selector = None

        self.file_selector = file_selection.FileSelectionWidget()
        self.stack.addWidget(self.file_selector)
        self.stack.setCurrentWidget(self.file_selector)

    def restore_main_content(self):
        self.stack.setCurrentWidget(self.app_shell)
        if self.eula_prompt is not None:
            self.stack.removeWidget(self.eula_prompt)
            self.eula_prompt.deleteLater()
            self.eula_prompt = None
            
    def on_page_change(self, page_name: str):
        """
        Central navigation + data logic
        """
        if page_name == "Dashboard":
            pass

        elif page_name == "Scan":
            pass

        elif page_name == "Resume":
            pass

        elif page_name == "Portfolio":
            pass

        elif page_name == "Settings":
            pass

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
    else:
        # Displays file selector for now but this should be changed to the main menu screen or whatever the home window will be
        window.show_file_selector()

    window.show()
    sys.exit(app.exec_())
