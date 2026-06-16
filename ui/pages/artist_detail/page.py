from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.artist import ArtistService
from .actions import ArtistDetailActions
from .info_section import ArtistInfoSection
from .styles import ARTIST_DETAIL_STYLES


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

        self.setStyleSheet(ARTIST_DETAIL_STYLES)

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
        self.info_section.clean_tag_button.clicked.connect(
            self.actions.clean_tag_table
        )
        self.info_section.sort_tag_button.clicked.connect(
            self.actions.sort_tag_table
        )

    def set_artist(self, artist_id: int):
        self.actions.set_artist(artist_id)
