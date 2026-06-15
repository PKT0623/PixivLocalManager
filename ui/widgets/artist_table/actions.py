from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QInputDialog

from .columns import (
    COLUMN_FAVORITE,
    COLUMN_RATING,
    COLUMN_SHORTCUTS,
    COLUMN_SORT_FIELDS,
)


class ArtistTableActions:
    def __init__(self, table):
        self.table = table

    def open_folder(self, folder_path: str):
        folder_path = str(folder_path or "").strip()

        if not folder_path:
            return

        url = QUrl.fromLocalFile(folder_path)
        QDesktopServices.openUrl(url)

    def open_pixiv_page(self, pixiv_id: str):
        pixiv_id = str(pixiv_id or "").strip()

        if not pixiv_id:
            return

        url = QUrl(f"https://www.pixiv.net/users/{pixiv_id}")
        QDesktopServices.openUrl(url)

    def handle_header_clicked(self, column: int):
        sort_field = COLUMN_SORT_FIELDS.get(column)

        if sort_field is None:
            return

        modifiers = QApplication.keyboardModifiers()
        is_multi_sort = bool(modifiers & Qt.ShiftModifier)

        self.table.sort_requested.emit(
            sort_field,
            is_multi_sort,
        )

    def handle_cell_clicked(self, row: int, column: int):
        if column != COLUMN_FAVORITE:
            return

        if row < 0 or row >= len(self.table.artist_ids):
            return

        artist_id = self.table.artist_ids[row]

        if artist_id is None:
            return

        self.table.favorite_toggled.emit(int(artist_id))

    def handle_cell_double_clicked(self, row: int, column: int):
        if row < 0 or row >= len(self.table.artist_ids):
            return

        artist_id = self.table.artist_ids[row]

        if artist_id is None:
            return

        if column == COLUMN_RATING:
            self._handle_rating_double_clicked(
                row,
                int(artist_id),
            )
            return

        if column in (
            COLUMN_FAVORITE,
            COLUMN_SHORTCUTS,
        ):
            return

        self.table.artist_selected.emit(int(artist_id))

    def _handle_rating_double_clicked(
        self,
        row: int,
        artist_id: int,
    ):
        current_rating = 0

        if row < len(self.table.artists):
            current_rating = int(
                self.table.artists[row].get("rating", 0) or 0
            )

        rating_text, ok = QInputDialog.getText(
            self.table,
            "평점 수정",
            "평점 입력 (0~10)",
            text=str(current_rating),
        )

        if not ok:
            return

        rating_text = rating_text.strip()

        if not rating_text:
            return

        try:
            rating = int(rating_text)
        except ValueError:
            return

        if rating < 0 or rating > 10:
            return

        if rating == current_rating:
            return

        self.table.rating_changed.emit(
            artist_id,
            rating,
        )
