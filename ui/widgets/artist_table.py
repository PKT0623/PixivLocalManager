from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)


class ArtistTable(QTableWidget):
    artist_selected = Signal(int)
    sort_requested = Signal(str)

    STATUS_LABELS = {
        "active": "활성",
        "inactive": "비활성",
        "unknown": "미확인",
        "latest": "최신",
        "up_to_date": "최신",
        "need_update": "업데이트 필요",
        "updated": "업데이트 완료",
        "error": "오류",
    }

    COLUMN_SORT_FIELDS = {
        1: "artist_name",
        3: "folder_artwork_count",
        4: "update_status",
        5: "rating",
    }

    def __init__(self):
        super().__init__()

        self.artist_ids = []
        self.artists = []
        self.rating_display_mode = "stars"

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(7)

        self.setHorizontalHeaderLabels(
            [
                "No",
                "작가명",
                "Pixiv ID",
                "작품 수",
                "상태",
                "평점",
                "메모",
            ]
        )

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)

        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._handle_header_clicked)

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Stretch)

        self.setColumnWidth(5, 100)

        self.cellDoubleClicked.connect(self._handle_cell_double_clicked)

    def set_artists(self, artists: list[dict]):
        self.artists = artists
        self.setRowCount(0)
        self.artist_ids = []

        for index, artist in enumerate(artists, start=1):
            row = self.rowCount()
            self.insertRow(row)

            artist_id = artist.get("id")
            self.artist_ids.append(artist_id)

            self._set_item(row, 0, index)
            self._set_item(row, 1, artist.get("artist_name"))
            self._set_item(row, 2, artist.get("pixiv_id"))
            self._set_item(row, 3, artist.get("folder_artwork_count", 0))
            self._set_item(row, 4, artist.get("update_status"))
            self._set_item(row, 5, artist.get("rating", 0))
            self._set_item(row, 6, artist.get("memo"))

    def set_rating_display_mode(self, mode: str):
        if mode not in ("stars", "number"):
            return

        self.rating_display_mode = mode
        self.set_artists(self.artists)

    def _set_item(self, row: int, column: int, value):
        text = self._format_value(column, value)

        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        if column in (0, 3, 5):
            item.setTextAlignment(Qt.AlignCenter)

        self.setItem(row, column, item)

    def _format_value(self, column: int, value) -> str:
        if column == 4:
            return self._format_status(value)

        if column == 5:
            return self._format_rating(value)

        if value is None or value == "":
            return "-"

        return str(value)

    def _format_status(self, value) -> str:
        if value is None or value == "":
            return "-"

        return self.STATUS_LABELS.get(str(value), str(value))

    def _format_rating(self, value) -> str:
        try:
            rating = int(value)
        except (TypeError, ValueError):
            rating = 0

        rating = max(0, min(10, rating))

        if self.rating_display_mode == "number":
            return f"{rating}/10"

        return self._rating_to_stars(rating)

    def _rating_to_stars(self, rating: int) -> str:
        if rating <= 0:
            return "-"

        full_stars = rating // 2
        has_half_score = rating % 2 == 1

        stars = "★" * full_stars

        if has_half_score:
            stars += "☆"

        return stars

    def _handle_header_clicked(self, column: int):
        sort_field = self.COLUMN_SORT_FIELDS.get(column)

        if sort_field is None:
            return

        self.sort_requested.emit(sort_field)

    def _handle_cell_double_clicked(self, row: int, column: int):
        if row < 0 or row >= len(self.artist_ids):
            return

        artist_id = self.artist_ids[row]

        if artist_id is None:
            return

        self.artist_selected.emit(int(artist_id))
