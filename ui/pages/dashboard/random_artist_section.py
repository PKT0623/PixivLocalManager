import random
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class RandomArtistSection(QFrame):
    def __init__(self):
        super().__init__()

        self.current_artists = []
        self.random_artist = None

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()

        title_label = QLabel("랜덤 작가")
        title_label.setObjectName("sectionTitle")

        random_button = QPushButton("랜덤 선택")
        random_button.clicked.connect(self.select_random_artist)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(random_button)

        random_card = QFrame()
        random_card.setObjectName("randomCard")

        card_layout = QVBoxLayout(random_card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        hidden_label = QLabel("???")
        hidden_label.setObjectName("randomHiddenText")
        hidden_label.setAlignment(Qt.AlignCenter)

        self.random_status_label = QLabel("아직 선택된 작가가 없습니다.")
        self.random_status_label.setObjectName("subText")
        self.random_status_label.setAlignment(Qt.AlignCenter)
        self.random_status_label.setWordWrap(True)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.random_folder_button = QPushButton("폴더 열기")
        self.random_pixiv_button = QPushButton("Pixiv 열기")

        self.random_folder_button.setEnabled(False)
        self.random_pixiv_button.setEnabled(False)

        self.random_folder_button.clicked.connect(self.open_random_folder)
        self.random_pixiv_button.clicked.connect(self.open_random_pixiv)

        button_layout.addWidget(self.random_folder_button)
        button_layout.addWidget(self.random_pixiv_button)

        card_layout.addStretch()
        card_layout.addWidget(hidden_label)
        card_layout.addWidget(self.random_status_label)
        card_layout.addLayout(button_layout)
        card_layout.addStretch()

        layout.addLayout(header_layout)
        layout.addWidget(random_card, 1)

    def update_artists(self, artists: list[dict]):
        self.current_artists = artists
        self.clear_random_artist()

    def select_random_artist(self):
        if not self.current_artists:
            self.random_artist = None
            self.random_status_label.setText("선택할 작가가 없습니다.")
            self.random_folder_button.setEnabled(False)
            self.random_pixiv_button.setEnabled(False)
            return

        self.random_artist = random.choice(self.current_artists)
        folder_exists = self._artist_folder_exists(self.random_artist)
        pixiv_exists = bool(
            str(self.random_artist.get("pixiv_id", "") or "").strip()
        )

        self.random_status_label.setText(
            "랜덤 작가가 선택되었습니다.\n정체를 확인하려면 열어보세요."
        )
        self.random_folder_button.setEnabled(folder_exists)
        self.random_pixiv_button.setEnabled(pixiv_exists)

    def clear_random_artist(self):
        self.random_artist = None
        self.random_status_label.setText("아직 선택된 작가가 없습니다.")
        self.random_folder_button.setEnabled(False)
        self.random_pixiv_button.setEnabled(False)

    def open_random_folder(self):
        if self.random_artist is None:
            return

        self._open_artist_folder(self.random_artist)

    def open_random_pixiv(self):
        if self.random_artist is None:
            return

        self._open_artist_pixiv(self.random_artist)

    def _artist_folder_exists(
        self,
        artist: dict,
    ) -> bool:
        folder_path = str(artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return False

        return Path(folder_path).exists()

    def _open_artist_folder(self, artist: dict):
        folder_path = str(artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        folder = Path(folder_path)

        if not folder.exists():
            self.random_folder_button.setEnabled(False)
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _open_artist_pixiv(self, artist: dict):
        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        QDesktopServices.openUrl(QUrl(f"https://www.pixiv.net/users/{pixiv_id}"))
