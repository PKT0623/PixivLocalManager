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

    def get_int_setting(
        self,
        key: str,
        default: int,
    ) -> int:
        value = self.get_setting(key)

        if value is None or value == "":
            return default

        try:
            return int(value)
        except (TypeError, ValueError):
            return default

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
            "pixiv_request_interval_min": 3,
            "pixiv_request_interval_max": 6,
            "pixiv_retry_count": 2,
            "pixiv_retry_interval": 5,
        }

        for key, value in default_settings.items():
            self.repo.set(key, value)

        return self.repo.get_all()
