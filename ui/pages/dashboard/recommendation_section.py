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


class HorizontalWheelScrollArea(QScrollArea):
    def wheelEvent(self, event):
        horizontal_bar = self.horizontalScrollBar()
        delta = event.angleDelta().y()

        if delta == 0:
            super().wheelEvent(event)
            return

        horizontal_bar.setValue(horizontal_bar.value() - delta)
        event.accept()


class RecommendationSection(QFrame):
    RECOMMENDATION_LIMIT = 20

    def __init__(self):
        super().__init__()

        self.current_artists = []
        self.current_mode = "high_rated"
        self.mode_buttons = {}

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()

        title_label = QLabel("작가 추천")
        title_label.setObjectName("sectionTitle")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        self._add_mode_button(
            parent_layout=button_layout,
            key="high_rated",
            text="고평점",
        )
        self._add_mode_button(
            parent_layout=button_layout,
            key="favorite",
            text="즐겨찾기",
        )

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self.refresh_recommendations)

        button_layout.addWidget(self.refresh_button)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)

        scroll_area = HorizontalWheelScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.recommendation_layout = QHBoxLayout(scroll_content)
        self.recommendation_layout.setContentsMargins(0, 0, 0, 0)
        self.recommendation_layout.setSpacing(10)

        scroll_area.setWidget(scroll_content)

        layout.addLayout(header_layout)
        layout.addWidget(scroll_area, 1)

        self._update_mode_buttons()

    def _add_mode_button(
        self,
        parent_layout: QHBoxLayout,
        key: str,
        text: str,
    ):
        button = QPushButton(text)
        button.setObjectName("limitButton")
        button.clicked.connect(
            lambda checked=False, value=key: self.set_mode(value)
        )

        self.mode_buttons[key] = button
        parent_layout.addWidget(button)

    def set_mode(
        self,
        mode: str,
    ):
        self.current_mode = mode
        self._update_mode_buttons()
        self.update_recommendations(self.current_artists)

    def refresh_recommendations(self):
        self.update_recommendations(self.current_artists)

    def _update_mode_buttons(self):
        for mode, button in self.mode_buttons.items():
            is_active = mode == self.current_mode
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def update_recommendations(
        self,
        artists: list[dict],
    ):
        self.current_artists = artists
        clear_layout(self.recommendation_layout)

        recommendations = self._pick_recommendations(artists)

        if not recommendations:
            return

        for artist in recommendations:
            self.recommendation_layout.addWidget(
                RecommendationCard(
                    artist=artist,
                )
            )

        self.recommendation_layout.addStretch()

    def _pick_recommendations(
        self,
        artists: list[dict],
    ) -> list[dict]:
        candidates = self._get_candidates(artists)

        return random.sample(
            candidates,
            min(self.RECOMMENDATION_LIMIT, len(candidates)),
        )

    def _get_candidates(
        self,
        artists: list[dict],
    ) -> list[dict]:
        if self.current_mode == "favorite":
            return [
                artist
                for artist in artists
                if bool(artist.get("is_favorite", 0))
            ]

        return [
            artist
            for artist in artists
            if to_int(artist.get("rating", 0), maximum=10) >= 8
        ]
