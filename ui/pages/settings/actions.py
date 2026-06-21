from app.services.backup import DatabaseBackupService
from app.services.database_info_service import DatabaseInfoService
from app.services.database_integrity_service import DatabaseIntegrityService
from app.services.database_maintenance_service import (
    DatabaseMaintenanceService,
)
from app.services.pixiv import PixivSessionService
from app.services.settings_backup_service import SettingsBackupService

from .action_parts import (
    SettingsBackupActions,
    SettingsCommonActions,
    SettingsDatabaseActions,
    SettingsEnvironmentActions,
    SettingsLoadActions,
    SettingsPixivActions,
    SettingsRequestActions,
)


class SettingsActions(
    SettingsLoadActions,
    SettingsPixivActions,
    SettingsRequestActions,
    SettingsDatabaseActions,
    SettingsBackupActions,
    SettingsEnvironmentActions,
    SettingsCommonActions,
):
    def __init__(self, page):
        self.page = page
        self.database_backup_service = DatabaseBackupService()
        self.database_info_service = DatabaseInfoService()
        self.database_integrity_service = DatabaseIntegrityService()
        self.database_maintenance_service = DatabaseMaintenanceService()
        self.settings_backup_service = SettingsBackupService()
        self.pixiv_session_service = PixivSessionService()
