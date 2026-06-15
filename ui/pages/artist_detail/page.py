from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
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

        self.rescan_button = QPushButton("현재 작가 재스캔")
        self.rescan_button.setObjectName("normalButton")

        self.check_update_button = QPushButton("업데이트 확인")
        self.check_update_button.setObjectName("normalButton")

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.setObjectName("refreshButton")

        self.save_button = QPushButton("저장")
        self.save_button.setObjectName("saveButton")

        self.back_button = QPushButton("← 작가 목록")
        self.back_button.setObjectName("backButton")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.rescan_button)
        header_layout.addWidget(self.check_update_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.back_button)

        self.info_section = ArtistInfoSection()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.info_section)

        layout.addLayout(header_layout)
        layout.addWidget(self.scroll_area, 1)

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
            QPushButton#refreshButton,
            QPushButton#saveButton,
            QPushButton#normalButton,
            QPushButton#folderSelectButton,
            QPushButton#copyButton,
            QPushButton#artworkButton,
            QPushButton#smallActionButton,
            QPushButton#tagButton {
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

            QPushButton#normalButton {
                min-width: 120px;
            }

            QPushButton#refreshButton,
            QPushButton#folderSelectButton,
            QPushButton#tagButton {
                min-width: 90px;
            }

            QPushButton#copyButton {
                min-width: 60px;
                padding: 6px 12px;
            }

            QPushButton#artworkButton {
                min-width: 110px;
                padding: 6px 12px;
            }

            QPushButton#smallActionButton {
                min-width: 60px;
                padding: 4px 10px;
            }

            QPushButton#backButton:hover,
            QPushButton#refreshButton:hover,
            QPushButton#normalButton:hover,
            QPushButton#folderSelectButton:hover,
            QPushButton#copyButton:hover,
            QPushButton#artworkButton:hover,
            QPushButton#smallActionButton:hover,
            QPushButton#tagButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#saveButton:hover {
                background-color: #157347;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QScrollArea > QWidget > QWidget {
                background-color: transparent;
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

            QCheckBox {
                font-size: 14px;
                spacing: 6px;
            }

            QTableWidget {
                border: 1px solid #dddddd;
                border-radius: 8px;
                background-color: #ffffff;
                font-size: 14px;
                gridline-color: #eeeeee;
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
        self.rescan_button.clicked.connect(self.actions.rescan_artist)
        self.check_update_button.clicked.connect(
            self.actions.check_artist_update
        )
        self.refresh_button.clicked.connect(self.actions.refresh_artist)
        self.save_button.clicked.connect(self.actions.save_artist)
        self.info_section.copy_folder_path_button.clicked.connect(
            self.actions.copy_folder_path
        )
        self.info_section.copy_pixiv_id_button.clicked.connect(
            self.actions.copy_pixiv_id
        )
        self.info_section.open_all_missing_artwork_button.clicked.connect(
            self.actions.open_all_missing_artworks
        )
        self.info_section.folder_select_button.clicked.connect(
            self.actions.select_folder
        )
        self.info_section.add_tag_button.clicked.connect(
            self.actions.add_tag_row
        )
        self.info_section.remove_tag_button.clicked.connect(
            self.actions.remove_selected_tag_row
        )

    def set_artist(self, artist_id: int):
        self.actions.set_artist(artist_id)
