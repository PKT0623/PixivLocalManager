import random

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .utils import clear_layout, find_latest_p0_image, to_int


class RecommendationSection(QFrame):
    def __init__(self):
        super().__init__()

        self.recommendation_limit = 10
        self.recommendation_limit_buttons = {}
        self.current_artists = []

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title_label = QLabel("작가 추천")
        title_label.setObjectName("sectionTitle")

        sub_label = QLabel("평점 8점 이상 작가 중 랜덤으로 추천합니다.")
        sub_label.setObjectName("subText")

        title_box.addWidget(title_label)
        title_box.addWidget(sub_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        for limit in (10, 20, 50):
            button = QPushButton(str(limit))
            button.setObjectName("limitButton")
            button.clicked.connect(
                lambda checked=False, value=limit: self.set_recommendation_limit(
                    value
                )
            )

            self.recommendation_limit_buttons[limit] = button
            button_layout.addWidget(button)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.recommendation_layout = QHBoxLayout(scroll_content)
        self.recommendation_layout.setContentsMargins(0, 0, 0, 0)
        self.recommendation_layout.setSpacing(12)

        scroll_area.setWidget(scroll_content)

        layout.addLayout(header_layout)
        layout.addWidget(scroll_area, 1)

        self._update_recommendation_limit_buttons()

    def set_recommendation_limit(self, limit: int):
        self.recommendation_limit = limit
        self._update_recommendation_limit_buttons()
        self.update_recommendations(self.current_artists)

    def _update_recommendation_limit_buttons(self):
        for limit, button in self.recommendation_limit_buttons.items():
            is_active = limit == self.recommendation_limit
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def update_recommendations(self, artists: list[dict]):
        self.current_artists = artists
        clear_layout(self.recommendation_layout)

        high_rated_artists = [
            artist
            for artist in artists
            if to_int(artist.get("rating", 0), maximum=10) >= 8
        ]

        recommendations = random.sample(
            high_rated_artists,
            min(self.recommendation_limit, len(high_rated_artists)),
        )

        if not recommendations:
            empty_label = QLabel("평점 8점 이상 추천 대상 작가가 없습니다.")
            empty_label.setObjectName("subText")
            self.recommendation_layout.addWidget(empty_label)
            return

        for artist in recommendations:
            self.recommendation_layout.addWidget(
                self._create_artist_recommend_card(artist)
            )

        self.recommendation_layout.addStretch()

    def _create_artist_recommend_card(self, artist: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("artistCard")
        card.setFixedWidth(190)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        thumbnail = QLabel("이미지 없음")
        thumbnail.setObjectName("thumbnailLabel")
        thumbnail.setAlignment(Qt.AlignCenter)
        thumbnail.setFixedSize(160, 110)

        image_path = find_latest_p0_image(artist.get("folder_path"))
        if image_path:
            pixmap = QPixmap(str(image_path))
            thumbnail.setPixmap(
                pixmap.scaled(
                    thumbnail.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        name_label = QLabel(str(artist.get("artist_name", "") or "-"))
        name_label.setObjectName("artistName")
        name_label.setWordWrap(True)

        info_label = QLabel(
            f"평점 {to_int(artist.get('rating', 0), maximum=10)}"
            f" / 작품 {to_int(artist.get('folder_artwork_count', 0))}"
        )
        info_label.setObjectName("artistInfo")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        folder_button = QPushButton("폴더")
        pixiv_button = QPushButton("Pixiv")

        folder_button.clicked.connect(
            lambda checked=False, target=artist: self._open_artist_folder(target)
        )
        pixiv_button.clicked.connect(
            lambda checked=False, target=artist: self._open_artist_pixiv(target)
        )

        pixiv_button.setEnabled(bool(str(artist.get("pixiv_id", "") or "").strip()))

        button_layout.addWidget(folder_button)
        button_layout.addWidget(pixiv_button)

        layout.addWidget(thumbnail, alignment=Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(info_label)
        layout.addLayout(button_layout)

        return card

    def _open_artist_folder(self, artist: dict):
        folder_path = str(artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    def _open_artist_pixiv(self, artist: dict):
        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        QDesktopServices.openUrl(QUrl(f"https://www.pixiv.net/users/{pixiv_id}"))
