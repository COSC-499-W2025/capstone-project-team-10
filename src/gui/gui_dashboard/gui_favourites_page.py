"""
src/gui/gui_dashboard/gui_favourites_page.py
--------------------------------------------
Shows all favourited projects across every log file.

Each row displays:
  • Project ID
  • Log file the project belongs to
  • A "Remove" button to un-favourite

Double-clicking a row fires  `project_clicked(project_id, log_path)`  so the
container can navigate straight to that project's LogDetailsPage.
"""

from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap

import utils.favourites as fav_store
import utils.project_thumbnails as pt

_THUMBNAIL_SIZE = 48          # smaller than the LogDetailsPage thumbnails
_DANGER_BTN_STYLE = """
    QPushButton {
        background-color: #c0392b;
        color: white;
        border: none;
        padding: 6px 14px;
        border-radius: 4px;
        font-size: 13px;
    }
    QPushButton:hover { background-color: #e74c3c; }
"""


def _make_thumbnail(project_id: str, size: int = _THUMBNAIL_SIZE) -> QPixmap:
    thumb_path = pt.get_thumbnail(project_id)
    if thumb_path and Path(thumb_path).is_file():
        px = QPixmap(thumb_path)
        if not px.isNull():
            return px.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    return px


class FavouritesPage(QWidget):
    """
    Signals
    -------
    project_clicked(project_id: str, log_path: Path)
        Emitted when the user double-clicks a row.
    """

    project_clicked = pyqtSignal(str, object)   # project_id, log_path (Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white;")
        self._init_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ── header ──────────────────────────────────────────────────────
        title = QLabel("Favourite Projects")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        layout.addWidget(title)

        # ── empty-state label (hidden when there are rows) ───────────────
        self._empty_label = QLabel("No favourites yet.\nOpen a log, then star a project to add it here.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet("color: #aaa; font-size: 14px;")
        layout.addWidget(self._empty_label)

        # ── table ────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", "Project ID", "Log File", ""])

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Fixed)          # thumbnail
        self.table.setColumnWidth(0, _THUMBNAIL_SIZE + 8)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)        # project id
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # log name
        hdr.setSectionResizeMode(3, QHeaderView.Fixed)          # remove btn
        self.table.setColumnWidth(3, 100)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setIconSize(QSize(_THUMBNAIL_SIZE, _THUMBNAIL_SIZE))
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e0e0e0;
                border: none;
                color: black;
            }
            QHeaderView::section {
                background-color: white;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: normal;
                color: #666;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #002145;
                color: white;
            }
        """)

        # Double-click anywhere on a row → open that project
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)

        layout.addWidget(self.table)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def refresh(self):
        """Re-read the favourites store and repopulate the table."""
        self.table.setRowCount(0)
        favourites = fav_store.get_favourites()

        self._empty_label.setVisible(len(favourites) == 0)
        self.table.setVisible(len(favourites) > 0)

        for idx, entry in enumerate(favourites):
            project_id = entry["project_id"]
            log_path_str = entry["log_path"]
            log_path = Path(log_path_str)
            log_name = log_path.name

            self.table.insertRow(idx)
            self.table.setRowHeight(idx, _THUMBNAIL_SIZE + 8)

            # Col 0 – thumbnail
            thumb_item = QTableWidgetItem()
            thumb_item.setIcon(QIcon(_make_thumbnail(project_id)))
            self.table.setItem(idx, 0, thumb_item)

            # Col 1 – project id (carry full log_path as UserRole data)
            pid_item = QTableWidgetItem(project_id)
            pid_item.setData(Qt.UserRole, log_path)
            self.table.setItem(idx, 1, pid_item)

            # Col 2 – log file name
            self.table.setItem(idx, 2, QTableWidgetItem(log_name))

            # Col 3 – remove button (inline widget)
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet(_DANGER_BTN_STYLE)
            # Capture current values in the lambda default args
            remove_btn.clicked.connect(
                lambda checked, pid=project_id, lp=log_path: self._on_remove(pid, lp)
            )
            self.table.setCellWidget(idx, 3, remove_btn)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_row_double_clicked(self, row: int, _col: int):
        pid_item = self.table.item(row, 1)
        if pid_item is None:
            return
        project_id = pid_item.text()
        log_path: Path = pid_item.data(Qt.UserRole)
        if log_path and log_path.exists():
            self.project_clicked.emit(project_id, log_path)
        else:
            QMessageBox.warning(
                self,
                "Log Not Found",
                f"The log file for project '{project_id}' could not be found:\n{log_path}",
            )

    def _on_remove(self, project_id: str, log_path: Path):
        """Un-favourite a project after confirmation."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Remove Favourite")
        msg.setText(f"Remove <b>{project_id}</b> from favourites?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("QLabel { color: black; font-weight: normal; }")
        btn_style = """
            QPushButton {
                background-color: #002145;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #003366; }
        """
        for button in msg.buttons():
            button.setStyleSheet(btn_style)
        if msg.exec_() == QMessageBox.Yes:
            fav_store.remove_favourite(project_id, log_path)
            self.refresh()