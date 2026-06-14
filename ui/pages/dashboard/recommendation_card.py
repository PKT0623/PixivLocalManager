from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from .utils import find_latest_p0_image, to_int


class RecommendationCard(QFrame):
    def __init__(self, artist: dict):
        super().__init__()

        self.artist = artist

        self.setObjectName("artistCard")
        self.setFixedWidth(190)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        thumbnail = QLabel("이미지 없음")
        thumbnail.setObjectName("thumbnailLabel")
        thumbnail.setAlignment(Qt.AlignCenter)
        thumbnail.setFixedSize(160, 110)

        image_path = find_latest_p0_image(self.artist.get("folder_path"))
        if image_path:
            pixmap = QPixmap(str(image_path))
            thumbnail.setPixmap(
                pixmap.scaled(
                    thumbnail.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        name_label = QLabel(str(self.artist.get("artist_name", "") or "-"))
        name_label.setObjectName("artistName")
        name_label.setWordWrap(True)

        info_label = QLabel(
            f"평점 {to_int(self.artist.get('rating', 0), maximum=10)}"
            f" / 작품 {to_int(self.artist.get('folder_artwork_count', 0))}"
        )
        info_label.setObjectName("artistInfo")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        folder_button = QPushButton("폴더")
        pixiv_button = QPushButton("Pixiv")

        folder_button.clicked.connect(self.open_artist_folder)
        pixiv_button.clicked.connect(self.open_artist_pixiv)

        pixiv_button.setEnabled(
            bool(str(self.artist.get("pixiv_id", "") or "").strip())
        )

        button_layout.addWidget(folder_button)
        button_layout.addWidget(pixiv_button)

        layout.addWidget(thumbnail, alignment=Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(info_label)
        layout.addLayout(button_layout)

    def open_artist_folder(self):
        folder_path = str(self.artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    def open_artist_pixiv(self):
        pixiv_id = str(self.artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        QDesktopServices.openUrl(QUrl(f"https://www.pixiv.net/users/{pixiv_id}"))
