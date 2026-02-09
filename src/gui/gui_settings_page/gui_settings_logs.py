from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QLineEdit, QSizePolicy, QVBoxLayout, QWidget

import src.param.param as param


class LoggingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        form_layout = QFormLayout()
        form_layout.setAlignment(Qt.AlignLeft)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        self.log_max_count = QLineEdit(str(param.get("logging.log_max_count")))
        form_layout.addRow("Number of previous sessions to store:", self.log_max_count)
        self.log_max_count.editingFinished.connect(self.update_log_max_count)

        self.current_log_file = QLineEdit(param.get("logging.current_log_file"))
        form_layout.addRow("Current Log File:", self.current_log_file)
        self.current_log_file.editingFinished.connect(self.update_current_log_file)

        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setMaximumWidth(3000)

        main_layout = QVBoxLayout()
        main_layout.addWidget(form_container)
        main_layout.setAlignment(form_container, Qt.AlignLeft | Qt.AlignTop)

        self.setLayout(main_layout)

    def update_log_max_count(self):
        new_max_count = self.log_max_count.text().strip()
        if new_max_count.isdigit():
            param.set("logging.log_max_count", int(new_max_count))
        else:
            # Reset to previous value if input is invalid
            self.log_max_count.setText(str(param.get("logging.log_max_count")))

    def update_current_log_file(self):
        new_log_file = self.current_log_file.text().strip()
        if new_log_file:
            param.set("logging.current_log_file", new_log_file)
