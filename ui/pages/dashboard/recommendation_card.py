from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from .utils import find_latest_p0_image, format_count, to_int


class RecommendationCard(QFrame):
    PIXMAP_CACHE = {}

    def __init__(
        self,
        artist: dict,
        badge_text: str = "",
    ):
        super().__init__()

        self.artist = artist
        self.badge_text = badge_text

        self.setObjectName("artistCard")
        self.setFixedWidth(260)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(7)

        thumbnail = QLabel("이미지 없음")
        thumbnail.setObjectName("thumbnailLabel")
        thumbnail.setAlignment(Qt.AlignCenter)
        thumbnail.setFixedSize(232, 190)

        pixmap = self._get_thumbnail_pixmap(thumbnail.size())

        if pixmap is not None:
            thumbnail.setPixmap(pixmap)

        artist_name = str(self.artist.get("artist_name", "") or "-")
        name_label = QLabel(self._shorten_text(artist_name, limit=24))
        name_label.setObjectName("artistName")
        name_label.setToolTip(artist_name)
        name_label.setWordWrap(True)

        pixiv_id = str(self.artist.get("pixiv_id", "") or "-")
        pixiv_label = QLabel(f"ID {pixiv_id}")
        pixiv_label.setObjectName("artistMeta")
        pixiv_label.setToolTip(pixiv_id)

        rating = to_int(self.artist.get("rating", 0), maximum=10)
        artwork_count = to_int(self.artist.get("folder_artwork_count", 0))
        file_count = to_int(self.artist.get("folder_file_count", 0))

        rating_label = QLabel(f"평점 {rating}")
        rating_label.setObjectName("artistInfo")

        artwork_label = QLabel(f"작품 {format_count(artwork_count)}")
        artwork_label.setObjectName("artistInfo")

        file_label = QLabel(f"파일 {format_count(file_count)}")
        file_label.setObjectName("artistInfo")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        self.folder_button = QPushButton("폴더")
        self.pixiv_button = QPushButton("Pixiv")

        self.folder_button.clicked.connect(self.open_artist_folder)
        self.pixiv_button.clicked.connect(self.open_artist_pixiv)

        self.folder_button.setEnabled(self._artist_folder_exists())
        self.pixiv_button.setEnabled(
            bool(str(self.artist.get("pixiv_id", "") or "").strip())
        )

        button_layout.addWidget(self.folder_button)
        button_layout.addWidget(self.pixiv_button)

        layout.addWidget(thumbnail, alignment=Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(pixiv_label)
        layout.addWidget(rating_label)
        layout.addWidget(artwork_label)
        layout.addWidget(file_label)
        layout.addStretch()
        layout.addLayout(button_layout)

    def open_artist_folder(self):
        folder_path = str(self.artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        folder = Path(folder_path)

        if not folder.exists():
            self.folder_button.setEnabled(False)
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def open_artist_pixiv(self):
        pixiv_id = str(self.artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        QDesktopServices.openUrl(QUrl(f"https://www.pixiv.net/users/{pixiv_id}"))

    def _artist_folder_exists(self) -> bool:
        folder_path = str(self.artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return False

        return Path(folder_path).exists()

    def _get_thumbnail_pixmap(
        self,
        target_size,
    ):
        folder_path = str(self.artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return None

        cache_key = f"{folder_path}:{target_size.width()}x{target_size.height()}"

        if cache_key in self.PIXMAP_CACHE:
            return self.PIXMAP_CACHE[cache_key]

        image_path = find_latest_p0_image(folder_path)

        if image_path is None:
            self.PIXMAP_CACHE[cache_key] = None
            return None

        pixmap = QPixmap(str(image_path))

        if pixmap.isNull():
            self.PIXMAP_CACHE[cache_key] = None
            return None

        scaled_pixmap = pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.PIXMAP_CACHE[cache_key] = scaled_pixmap

        return scaled_pixmap

    def _shorten_text(
        self,
        text: str,
        limit: int,
    ) -> str:
        if len(text) <= limit:
            return text

        return f"{text[:limit]}..."
