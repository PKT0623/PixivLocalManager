from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from .columns import COLUMN_FAVORITE, COLUMN_SHORTCUTS, COLUMN_SORT_FIELDS


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

        self.table.sort_requested.emit(sort_field)

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
        if column in (
            COLUMN_FAVORITE,
            COLUMN_SHORTCUTS,
        ):
            return

        if row < 0 or row >= len(self.table.artist_ids):
            return

        artist_id = self.table.artist_ids[row]

        if artist_id is None:
            return

        self.table.artist_selected.emit(int(artist_id))
