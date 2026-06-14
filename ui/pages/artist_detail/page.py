from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.artist_service import ArtistService

from .actions import ArtistDetailActions
from .info_section import ArtistInfoSection


class ArtistDetailPage(QWidget):
    back_requested = Signal()
    artist_updated = Signal(int)

    def __init__(self):
        super().__init__()

        self.artist_id = None
        self.current_artist = None
        self.artist_service = ArtistService()
        self.actions = ArtistDetailActions(self)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()

        self.title_label = QLabel("작가 상세")
        self.title_label.setObjectName("pageTitle")

        self.save_button = QPushButton("저장")
        self.save_button.setObjectName("saveButton")

        self.back_button = QPushButton("← 작가 목록")
        self.back_button.setObjectName("backButton")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.back_button)

        self.info_section = ArtistInfoSection()

        layout.addLayout(header_layout)
        layout.addWidget(self.info_section)
        layout.addStretch()

        self.setStyleSheet(
            """
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
                margin-top: 8px;
            }

            QFrame#infoFrame {
                border: 1px solid #dddddd;
                border-radius: 8px;
                background-color: #ffffff;
            }

            QPushButton#backButton,
            QPushButton#saveButton,
            QPushButton#folderSelectButton {
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#saveButton {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
                min-width: 80px;
            }

            QPushButton#backButton {
                min-width: 120px;
            }

            QPushButton#folderSelectButton {
                min-width: 100px;
            }

            QPushButton#backButton:hover,
            QPushButton#folderSelectButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#saveButton:hover {
                background-color: #157347;
            }

            QLineEdit {
                border: 1px solid #dddddd;
                border-radius: 6px;
                padding: 6px 8px;
                background-color: #ffffff;
                font-size: 14px;
            }

            QLineEdit:read-only {
                background-color: #f9f9f9;
            }

            QTextEdit {
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 8px;
                background-color: #ffffff;
                font-size: 14px;
            }
            """
        )

    def _connect_signals(self):
        self.back_button.clicked.connect(self.back_requested.emit)
        self.save_button.clicked.connect(self.actions.save_artist)
        self.info_section.folder_select_button.clicked.connect(
            self.actions.select_folder
        )

    def set_artist(self, artist_id: int):
        self.actions.set_artist(artist_id)
