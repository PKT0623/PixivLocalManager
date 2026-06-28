from typing import Any, Optional

from app.database.app_setting_repository import AppSettingRepository

from .constants import (
    BOOL_SETTING_KEYS,
    DEFAULT_SCAN_IMAGE_EXTENSIONS,
    INT_SETTING_RULES,
    PRESERVED_SETTING_KEYS_ON_RESET,
    SCAN_IMAGE_EXTENSIONS_KEY,
)
from .scan_settings import ScanSettingsMixin
from .value_parser import SettingsValueParserMixin


class SettingsService(
    ScanSettingsMixin,
    SettingsValueParserMixin,
):
    SCAN_IMAGE_EXTENSIONS_KEY = SCAN_IMAGE_EXTENSIONS_KEY
    DEFAULT_SCAN_IMAGE_EXTENSIONS = DEFAULT_SCAN_IMAGE_EXTENSIONS
    PRESERVED_SETTING_KEYS_ON_RESET = PRESERVED_SETTING_KEYS_ON_RESET
    INT_SETTING_RULES = INT_SETTING_RULES
    BOOL_SETTING_KEYS = BOOL_SETTING_KEYS

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
        normalized_value = self.normalize_setting_value(
            key=key,
            value=value,
        )

        return self.repo.set(key, normalized_value)

    def delete_setting(
        self,
        key: str,
    ):
        return self.repo.delete(key)

    def reset_to_default(self):
        preserved_settings = self._collect_preserved_settings()

        self.repo.delete_all()

        for key, value in preserved_settings.items():
            self.set_setting(
                key,
                value,
            )

        default_settings = self.get_default_settings()

        for key, value in default_settings.items():
            self.set_setting(
                key,
                value,
            )

        return self.repo.get_all()

    def get_default_settings(self) -> dict:
        return {
            "scan_interval": 60,
            "auto_rescan": True,
            "theme": "light",
            "pixiv_request_interval_ms": 2000,
            "pixiv_batch_size": 1000,
            "pixiv_batch_rest_ms": 300000,
            "pixiv_retry_count": 3,
            "update_check_request_interval_ms": 1000,
            "update_check_batch_size": 100,
            "update_check_batch_rest_ms": 180000,
            "auto_backup_enabled": False,
            "auto_backup_interval_days": 7,
            "auto_backup_keep_count": 10,
            self.SCAN_IMAGE_EXTENSIONS_KEY: ",".join(
                self.DEFAULT_SCAN_IMAGE_EXTENSIONS
            ),
        }

    def _collect_preserved_settings(self) -> dict:
        preserved_settings = {}

        for key in self.PRESERVED_SETTING_KEYS_ON_RESET:
            value = self.get_setting(key)

            if value is None:
                continue

            preserved_settings[key] = value

        return preserved_settings
