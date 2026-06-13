from typing import Any, Optional

from app.database.app_setting_repository import AppSettingRepository


class SettingsService:
    def __init__(self):
        self.repo = AppSettingRepository()

    def get_all_settings(self):
        return self.repo.get_all()

    def get_setting(
        self,
        key: str,
    ) -> Optional[Any]:
        setting = self.repo.get(key)

        if setting is None:
            return None

        return setting.value

    def set_setting(
        self,
        key: str,
        value: Any,
    ):
        return self.repo.set(key, value)

    def delete_setting(
        self,
        key: str,
    ):
        return self.repo.delete(key)

    def reset_to_default(self):
        default_settings = {
            "scan_interval": 60,
            "auto_rescan": True,
            "theme": "light",
        }

        for key, value in default_settings.items():
            self.repo.set(key, value)

        return self.repo.get_all()
