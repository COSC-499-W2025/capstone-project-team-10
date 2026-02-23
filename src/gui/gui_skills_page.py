from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout , QHeaderView
)
from PyQt5.QtCore import Qt


class SkillsPage(QWidget):
    """
    Page that displays all unique skills and how many times they appear.
    """

    def __init__(self, resume_manager):
        super().__init__()

        self.manager = resume_manager
        self.setWindowTitle("Skills Overview")
        self.resize(800, 500)

        layout = QVBoxLayout(self)

        # ---- Title ----
        title = QLabel("Skills Demonstrated Across Projects")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        # ---- Sort Controls ----
        sort_layout = QHBoxLayout()

        self.sort_alpha_btn = QPushButton("Sort A–Z")
        self.sort_count_btn = QPushButton("Sort by Frequency")

        self.sort_alpha_btn.clicked.connect(self.sort_alphabetical)
        self.sort_count_btn.clicked.connect(self.sort_by_count)

        sort_layout.addWidget(self.sort_alpha_btn)
        sort_layout.addWidget(self.sort_count_btn)

        # ---- Table ----
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Skill", "Frequency"])
        header = self.table.horizontalHeader()

        # Skills column expands
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Frequency column auto-sizes to content (small)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(title)
        layout.addLayout(sort_layout)
        layout.addWidget(self.table)

        self.skill_counts = {}
        self.load_skills()

    # ------------------------------
    # Load + Count Skills
    # ------------------------------
    def load_skills(self):
        self.skill_counts.clear()

        for project_name in self.manager.projects.keys():
            skills_csv = self.manager.get_key_skills_csv(project_name)

            if skills_csv:
                skills = [s.strip() for s in skills_csv.split(",") if s.strip()]
                for skill in skills:
                    self.skill_counts[skill] = self.skill_counts.get(skill, 0) + 1

        self.populate_table(self.skill_counts)

    # ------------------------------
    # Populate Table
    # ------------------------------
    def populate_table(self, skill_dict):
        self.table.setRowCount(len(skill_dict))

        for row, (skill, count) in enumerate(skill_dict.items()):
            self.table.setItem(row, 0, QTableWidgetItem(skill))
            self.table.setItem(row, 1, QTableWidgetItem(str(count)))
            item = self.table.item(row, 1)
            item.setTextAlignment(Qt.AlignCenter)


    # ------------------------------
    # Sorting
    # ------------------------------
    def sort_alphabetical(self):
        sorted_dict = dict(sorted(self.skill_counts.items(), key=lambda x: x[0].lower()))
        self.populate_table(sorted_dict)

    def sort_by_count(self):
        sorted_dict = dict(sorted(self.skill_counts.items(), key=lambda x: x[1], reverse=True))
        self.populate_table(sorted_dict)