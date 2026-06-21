from PySide6.QtCore import QObject

from app.services.pixiv_update_service import PixivUpdateService
from app.services.settings_service import SettingsService

from .action_parts import (
    UpdateCheckControlActions,
    UpdateCheckStartActions,
    UpdateCheckUIStateActions,
    UpdateCheckUtilityActions,
    UpdateCheckWorkerHandlerActions,
)


class UpdateCheckActions(
    UpdateCheckStartActions,
    UpdateCheckControlActions,
    UpdateCheckWorkerHandlerActions,
    UpdateCheckUIStateActions,
    UpdateCheckUtilityActions,
    QObject,
):
    def __init__(self, page):
        super().__init__(page)

        self.page = page
        self.cancel_event = None
        self.pause_event = None
        self.settings_service = SettingsService()
        self.pixiv_update_service = PixivUpdateService()

        self.current_artist_ids = []
        self.resume_artist_ids = []
        self.progress_offset = 0
        self.total_count = 0
        self.current_summary = None
        self.is_paused = False
        self.is_cancel_requested = False
