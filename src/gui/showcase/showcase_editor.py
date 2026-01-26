import csv
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import src.log.log as log
import src.param.param as param
from src.fas.fas import FileAnalysis
from src.log.log_sorter import LogSorter


# TODO: Needs Styling
class ProjectEditor(QWidget):
    def __init__(self, log_entry: FileAnalysis, parent=None):
        super().__init__(parent)
        self.project: FileAnalysis = log_entry
        self.original_project: FileAnalysis = log_entry
        self._layout = QVBoxLayout()
        self.text_boxes = []

        # Create Text Boxes for each modifiable value
        # Project Title
        project_title = QTextEdit()
        project_title.setText(self.project.file_name)
        project_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._layout.addWidget(project_title)
        self.text_boxes.append(project_title)

        # Project Importance
        project_importance = QTextEdit()
        project_importance.setText(str(self.project.importance))
        project_importance.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._layout.addWidget(project_importance)
        self.text_boxes.append(project_importance)

        # Project active Dates

        project_date_start = QTextEdit()
        project_date_start.setText(f"{self.project.created_time}")
        project_date_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._layout.addWidget(project_date_start)
        self.text_boxes.append(project_date_start)

        project_date_end = QTextEdit()
        project_date_end.setText(f"{self.project.last_modified}")
        project_date_end.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._layout.addWidget(project_date_end)
        self.text_boxes.append(project_date_end)

        # Project Skills Data
        project_extra_data = QTextEdit()
        project_extra_data.setText(str(self.project.extra_data))
        project_extra_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._layout.addWidget(project_extra_data)
        self.text_boxes.append(project_extra_data)

        self.setLayout(self._layout)
        # Create a QTextEdit for each preset value
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def update_log(self):
        self.project.file_name = self.text_boxes[0].toPlainText()
        self.project.importance = float(self.text_boxes[1].toPlainText())
        self.project.created_time = self.text_boxes[2].toPlainText()
        self.project.last_modified = self.text_boxes[3].toPlainText()
        self.project.extra_data = self.text_boxes[4].toPlainText()

        # set update protection flag and force update
        self.project.customized = True
        log.update(self.project, True)


class ProjectEditWidget(QWidget):
    def __init__(self, page_num=0):
        super().__init__()
        self.projects: dict[Path, ProjectEditor] = dict()
        self.main_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.editors_container = QWidget()
        self.editors_layout = QVBoxLayout(self.editors_container)
        self.init_editor()

    def init_editor(self):
        self.scroll_area.setWidgetResizable(True)

        self.editors_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.editors_container)
        self.main_layout.addWidget(self.scroll_area, stretch=1)
        # For every line in the current log file, create a ProjectEditor
        log_file = Path(log.current_log_file)
        try:
            with open(log_file, "r", encoding="utf-8") as lf:
                reader = csv.reader(lf)
                next(reader)  # Skip header row
                for row in reader:
                    file_analysis: FileAnalysis = FileAnalysis(
                        row[0], row[1], row[2], row[3], row[4], row[5]
                    )
                    editor = ProjectEditor(file_analysis)
                    self.editors_layout.addWidget(editor)
                    self.projects[Path(file_analysis.file_path)] = editor
        except Exception as e:
            # This should never be hit, at all. If it is something is very wrong with log formatting
            # Reset the log file
            log.open_log_file()
            print(f"Error reading log file: {e} at {log_file}")
            return

        # Save Button
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Changes")
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        self.main_layout.addLayout(button_layout)

        # Connect the button to your save logic
        save_button.clicked.connect(self.save_changes)

    def reload_editor(self):
        # Remove all widgets and layouts from the main layout
        layout = self.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(None)
                    else:
                        sub_layout = item.layout()
                        if sub_layout is not None:
                            while sub_layout.count():
                                sub_item = sub_layout.takeAt(0)
                                if sub_item is not None:
                                    sub_widget = sub_item.widget()
                                    if sub_widget is not None:
                                        sub_widget.setParent(None)
        # Clear the projects dictionary
        self.projects.clear()
        # Re-initialize the editor area
        self.init_editor()

    def save_changes(self):
        # Iterate over all widgets in the editors layout
        for i in range(self.editors_layout.count()):
            item = self.editors_layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None and hasattr(widget, "update_log"):
                print(
                    "Updating project:",
                    widget.project.file_name,
                    "With changes",
                    widget.project.file_name,
                )
                widget.update_log()
        # Reload the editor to reflect changes
        self.reload_editor()
