from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import src.gui.gui_utils.gui_styles as styles
import src.param.param as param
from src.gui.gui_utils.gui_multifolder_selector import MultiFolderSelector
from src.gui.gui_utils.gui_multiselector import MultiSelector


class PersonalProfile(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        grid_layout = QGridLayout()
        grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)
        grid_layout.setContentsMargins(20, 20, 20, 20)

        # Set column stretch: labels (col 0) minimal, fields (col 1) expand
        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 1)

        # Name
        name_label = QLabel("Name:")
        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.name = QLineEdit(param.get("profile.name"))
        self.name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(name_label, 0, 0, alignment=Qt.AlignRight)
        grid_layout.addWidget(self.name, 0, 1)
        self.name.editingFinished.connect(self.update_name)

        # Email
        email_label = QLabel("Email:")
        email_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.email = QLineEdit(param.get("profile.email"))
        self.email.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(email_label, 1, 0, alignment=Qt.AlignRight)
        grid_layout.addWidget(self.email, 1, 1)
        self.email.editingFinished.connect(self.update_email)

        # Phone number
        phone_label = QLabel("Phone Number:")
        phone_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.phone_number = QLineEdit(param.get("profile.phone_number"))
        self.phone_number.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(phone_label, 2, 0, alignment=Qt.AlignRight)
        grid_layout.addWidget(self.phone_number, 2, 1)
        self.phone_number.editingFinished.connect(self.update_phone_number)

        # Github
        github_label = QLabel("Github URL:")
        github_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.github = QLineEdit(param.get("profile.github"))
        self.github.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(github_label, 3, 0, alignment=Qt.AlignRight)
        grid_layout.addWidget(self.github, 3, 1)
        self.github.editingFinished.connect(self.update_github)

        # Linkedin
        linkedin_label = QLabel("LinkedIn URL:")
        linkedin_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.linkedin = QLineEdit(param.get("profile.linkedin"))
        self.linkedin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(linkedin_label, 4, 0, alignment=Qt.AlignRight)
        grid_layout.addWidget(self.linkedin, 4, 1)
        self.linkedin.editingFinished.connect(self.update_linkedin)

        form_container = QWidget()
        form_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_container.setLayout(grid_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(form_container, stretch=1)
        main_layout.setStretch(0, 1)
        main_layout.setAlignment(form_container, Qt.AlignTop)

        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_name(self):
        new_name = self.name.text()
        if not param.set("profile.name", new_name):
            param.set("profile.name", "")
        self.name.setText(param.get("profile.name"))

    def update_email(self):
        new_email = self.email.text()
        if not param.set("profile.email", new_email):
            param.set("profile.email", "")
        self.email.setText(param.get("profile.email"))

    def update_phone_number(self):
        new_phone_number = self.phone_number.text()
        if not param.set("profile.phone_number", new_phone_number):
            param.set("profile.phone_number", "")
        self.phone_number.setText(param.get("profile.phone_number"))

    def update_github(self):
        new_github = self.github.text()
        if not param.set("profile.github", new_github):
            param.set("profile.github", "")
        self.github.setText(param.get("profile.github"))

    def update_linkedin(self):
        new_linkedin = self.linkedin.text()
        if not param.set("profile.linkedin", new_linkedin):
            param.set("profile.linkedin", "")
        self.linkedin.setText(param.get("profile.linkedin"))
