import webbrowser

from PySide6.QtWidgets import QHeaderView

from ..table_common import PixivManagerBaseTable
from .model import BookmarkArtworkTableModel


class BookmarkArtworkTable(PixivManagerBaseTable):
    def __init__(self):
        super().__init__()

        self.model_data = BookmarkArtworkTableModel()

        self._setup_ui()
        self.doubleClicked.connect(self._handle_double_clicked)

    def _setup_ui(self):
        self._setup_base_ui()

        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsClickable(True)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        header.setSectionResizeMode(10, QHeaderView.Fixed)
        header.setSectionResizeMode(11, QHeaderView.Fixed)

        self.setColumnWidth(0, 36)
        self.setColumnWidth(1, 300)
        self.setColumnWidth(2, 110)
        self.setColumnWidth(3, 150)
        self.setColumnWidth(4, 110)
        self.setColumnWidth(5, 70)
        self.setColumnWidth(6, 60)
        self.setColumnWidth(7, 400)
        self.setColumnWidth(8, 80)
        self.setColumnWidth(9, 130)
        self.setColumnWidth(10, 80)
        self.setColumnWidth(11, 80)

    def load_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
    ):
        self.model_data.load_bookmark_artworks(bookmark_artworks)

    def _open_pixiv(
        self,
        bookmark_artwork: dict,
    ):
        artwork_id = str(bookmark_artwork.get("artwork_id", "") or "")

        if not artwork_id:
            return

        webbrowser.open(f"https://www.pixiv.net/artworks/{artwork_id}")
