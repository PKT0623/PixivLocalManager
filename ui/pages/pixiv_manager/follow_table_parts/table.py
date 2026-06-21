import webbrowser

from PySide6.QtWidgets import QHeaderView

from ..table_common import PixivManagerBaseTable
from .model import FollowUserTableModel


class FollowUserTable(PixivManagerBaseTable):
    def __init__(self):
        super().__init__()

        self.model_data = FollowUserTableModel()

        self._setup_ui()
        self.doubleClicked.connect(self._handle_double_clicked)

    def _setup_ui(self):
        self._setup_base_ui()

        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsClickable(True)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        header.setSectionResizeMode(8, QHeaderView.Fixed)

        self.setColumnWidth(0, 36)
        self.setColumnWidth(1, 150)
        self.setColumnWidth(2, 110)
        self.setColumnWidth(3, 80)
        self.setColumnWidth(5, 80)
        self.setColumnWidth(6, 130)
        self.setColumnWidth(7, 80)
        self.setColumnWidth(8, 80)

    def load_follow_users(
        self,
        follow_users: list[dict],
    ):
        self.model_data.load_follow_users(follow_users)

    def _open_pixiv(
        self,
        follow_user: dict,
    ):
        pixiv_user_id = str(follow_user.get("pixiv_user_id", "") or "")

        if not pixiv_user_id:
            return

        webbrowser.open(f"https://www.pixiv.net/users/{pixiv_user_id}")
