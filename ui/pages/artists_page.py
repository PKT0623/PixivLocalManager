from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.artist_service import ArtistService
from ui.widgets.artist_table import ArtistTable


class ArtistsPage(QWidget):
    artist_selected = Signal(int)

    STATUS_SORT_ORDERS = [
        ["unknown", "up_to_date", "latest", "need_update", "updated", "error"],
        ["up_to_date", "latest", "need_update", "updated", "unknown", "error"],
        ["need_update", "updated", "unknown", "up_to_date", "latest", "error"],
    ]

    DEFAULT_SORT_REVERSE = {
        "artist_name": False,
        "folder_artwork_count": True,
        "rating": True,
    }

    def __init__(self):
        super().__init__()

        self.artist_service = ArtistService()
        self.all_artists = []
        self.rating_display_mode = "stars"

        self.sort_field = "artist_name"
        self.sort_reverse = False
        self.status_sort_index = 0

        self._setup_ui()
        self._connect_signals()

        self.load_artists()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title_label = QLabel("작가 목록")
        title_label.setObjectName("pageTitle")

        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("작가명 또는 Pixiv ID 검색")

        self.rating_toggle_button = QPushButton("평점: 별")
        self.refresh_button = QPushButton("새로고침")

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.rating_toggle_button)
        search_layout.addWidget(self.refresh_button)

        self.artist_table = ArtistTable()

        layout.addWidget(title_label)
        layout.addLayout(search_layout)
        layout.addWidget(self.artist_table, 1)

        self.setStyleSheet(
            """
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
            }

            QLineEdit {
                padding: 8px 10px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                font-size: 14px;
            }

            QPushButton {
                padding: 8px 14px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }
            """
        )

    def _connect_signals(self):
        self.search_input.textChanged.connect(self._filter_artists)
        self.rating_toggle_button.clicked.connect(self._toggle_rating_display)
        self.refresh_button.clicked.connect(self.load_artists)
        self.artist_table.artist_selected.connect(self.artist_selected.emit)
        self.artist_table.sort_requested.connect(self._handle_sort_requested)

    def load_artists(self):
        self.all_artists = self.artist_service.get_all_artists()
        self._apply_filter_and_sort()

    def _filter_artists(self, keyword: str):
        self._apply_filter_and_sort()

    def _apply_filter_and_sort(self):
        keyword = self.search_input.text().strip().lower()

        if not keyword:
            artists = list(self.all_artists)
        else:
            artists = []

            for artist in self.all_artists:
                artist_name = str(artist.get("artist_name", "")).lower()
                pixiv_id = str(artist.get("pixiv_id", "")).lower()

                if keyword in artist_name or keyword in pixiv_id:
                    artists.append(artist)

        artists = self._sort_artists(artists)
        self.artist_table.set_artists(artists)

    def _handle_sort_requested(self, sort_field: str):
        if sort_field == "update_status":
            self.sort_field = sort_field
            self.status_sort_index = (
                self.status_sort_index + 1
            ) % len(self.STATUS_SORT_ORDERS)
            self._apply_filter_and_sort()
            return

        if self.sort_field == sort_field:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_field = sort_field
            self.sort_reverse = self.DEFAULT_SORT_REVERSE.get(
                sort_field,
                False,
            )

        self._apply_filter_and_sort()

    def _sort_artists(self, artists: list[dict]) -> list[dict]:
        if self.sort_field is None:
            return artists

        if self.sort_field == "artist_name":
            return sorted(
                artists,
                key=lambda artist: str(
                    artist.get("artist_name", "")
                ).lower(),
                reverse=self.sort_reverse,
            )

        if self.sort_field == "folder_artwork_count":
            return sorted(
                artists,
                key=lambda artist: int(
                    artist.get("folder_artwork_count", 0) or 0
                ),
                reverse=self.sort_reverse,
            )

        if self.sort_field == "rating":
            return sorted(
                artists,
                key=lambda artist: int(
                    artist.get("rating", 0) or 0
                ),
                reverse=self.sort_reverse,
            )

        if self.sort_field == "update_status":
            return self._sort_by_status(artists)

        return artists

    def _sort_by_status(self, artists: list[dict]) -> list[dict]:
        status_order = self.STATUS_SORT_ORDERS[self.status_sort_index]

        status_rank = {
            status: index
            for index, status in enumerate(status_order)
        }

        return sorted(
            artists,
            key=lambda artist: status_rank.get(
                str(artist.get("update_status", "")),
                len(status_rank),
            ),
        )

    def _toggle_rating_display(self):
        if self.rating_display_mode == "stars":
            self.rating_display_mode = "number"
            self.rating_toggle_button.setText("평점: 숫자")
        else:
            self.rating_display_mode = "stars"
            self.rating_toggle_button.setText("평점: 별")

        self.artist_table.set_rating_display_mode(
            self.rating_display_mode
        )
