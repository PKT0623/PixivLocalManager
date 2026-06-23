from PySide6.QtCore import QObject

from app.services import BookmarkService, FollowService, SettingsService

from .action_parts import (
    PixivManagerDataActions,
    PixivManagerDeleteActions,
    PixivManagerImportActions,
    PixivManagerLogActions,
    PixivManagerPaginationActions,
    PixivManagerSelectionActions,
    PixivManagerWorkerActions,
)


class PixivManagerActions(
    QObject,
    PixivManagerDataActions,
    PixivManagerPaginationActions,
    PixivManagerImportActions,
    PixivManagerWorkerActions,
    PixivManagerSelectionActions,
    PixivManagerDeleteActions,
    PixivManagerLogActions,
):
    PAGE_SIZE_SETTING_KEY = "pixiv_manager_page_size"

    def __init__(self, page):
        QObject.__init__(self, page)

        self.page = page
        self.follow_service = FollowService()
        self.bookmark_service = BookmarkService()
        self.settings_service = SettingsService()

        self.follow_users = []
        self.bookmark_artworks = []

        self.current_page = 1
        self.filtered_items = []
