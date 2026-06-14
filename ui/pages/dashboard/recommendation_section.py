import random

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .recommendation_card import RecommendationCard
from .utils import clear_layout, to_int


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

        recommendations = self._pick_recommendations(artists)

        if not recommendations:
            empty_label = QLabel("평점 8점 이상 추천 대상 작가가 없습니다.")
            empty_label.setObjectName("subText")
            self.recommendation_layout.addWidget(empty_label)
            return

        for artist in recommendations:
            self.recommendation_layout.addWidget(
                RecommendationCard(artist)
            )

        self.recommendation_layout.addStretch()

    def _pick_recommendations(self, artists: list[dict]) -> list[dict]:
        high_rated_artists = [
            artist
            for artist in artists
            if to_int(artist.get("rating", 0), maximum=10) >= 8
        ]

        return random.sample(
            high_rated_artists,
            min(self.recommendation_limit, len(high_rated_artists)),
        )
