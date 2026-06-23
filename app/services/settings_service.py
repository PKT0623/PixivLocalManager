from typing import Any, Optional

from app.database.app_setting_repository import AppSettingRepository


class SettingsService:
    SCAN_IMAGE_EXTENSIONS_KEY = "scan_image_extensions"
    DEFAULT_SCAN_IMAGE_EXTENSIONS = [
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "bmp",
    ]

    PRESERVED_SETTING_KEYS_ON_RESET = {
        "pixiv_phpsessid",
        "pixiv_root_folder",
        "scan_root_folder",
        "last_scan_result",
        "recent_scan_history",
        "last_backup_at",
        "window_width",
        "window_height",
        "window_x",
        "window_y",
        "window_maximized",
    }

    INT_SETTING_RULES = {
        "pixiv_request_interval_ms": {
            "default": 2000,
            "minimum": 2000,
            "maximum": 600000,
        },
        "pixiv_batch_size": {
            "default": 1000,
            "minimum": 1,
            "maximum": 10000,
        },
        "pixiv_batch_rest_ms": {
            "default": 300000,
            "minimum": 0,
            "maximum": 3600000,
        },
        "pixiv_retry_count": {
            "default": 3,
            "minimum": 0,
            "maximum": 20,
        },
        "update_check_request_interval_ms": {
            "default": 1000,
            "minimum": 0,
            "maximum": 600000,
        },
        "update_check_batch_size": {
            "default": 100,
            "minimum": 1,
            "maximum": 1000,
        },
        "update_check_batch_rest_ms": {
            "default": 180000,
            "minimum": 0,
            "maximum": 3600000,
        },
        "auto_backup_interval_days": {
            "default": 7,
            "minimum": 1,
            "maximum": 365,
        },
        "auto_backup_keep_count": {
            "default": 10,
            "minimum": 1,
            "maximum": 999,
        },
        "window_width": {
            "default": 1500,
            "minimum": 800,
            "maximum": 10000,
        },
        "window_height": {
            "default": 900,
            "minimum": 600,
            "maximum": 10000,
        },
        "window_x": {
            "default": 0,
            "minimum": -10000,
            "maximum": 10000,
        },
        "window_y": {
            "default": 0,
            "minimum": -10000,
            "maximum": 10000,
        },
        "pixiv_manager_page_size": {
            "default": 50,
            "minimum": 10,
            "maximum": 5000,
        },
    }

    BOOL_SETTING_KEYS = {
        "auto_backup_enabled",
        "auto_rescan",
        "window_maximized",
    }

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
        rule = self.INT_SETTING_RULES.get(key)

        if value is None or value == "":
            return default

        try:
            parsed_value = int(value)
        except (TypeError, ValueError):
            return default

        if rule is None:
            return parsed_value

        return self.clamp_int(
            value=parsed_value,
            minimum=rule["minimum"],
            maximum=rule["maximum"],
        )

    def get_bool_setting(
        self,
        key: str,
        default: bool = False,
    ) -> bool:
        value = self.get_setting(key)

        if value is None:
            return default

        normalized_value = str(value).strip().lower()

        if normalized_value in {
            "1",
            "true",
            "yes",
            "on",
        }:
            return True

        if normalized_value in {
            "0",
            "false",
            "no",
            "off",
        }:
            return False

        return default

    def get_scan_image_extensions(self) -> list[str]:
        value = self.get_setting(self.SCAN_IMAGE_EXTENSIONS_KEY)

        if value is None or str(value).strip() == "":
            return list(self.DEFAULT_SCAN_IMAGE_EXTENSIONS)

        extensions = self.normalize_scan_image_extensions(value)

        if not extensions:
            return list(self.DEFAULT_SCAN_IMAGE_EXTENSIONS)

        return extensions

    def set_scan_image_extensions(
        self,
        extensions,
    ):
        normalized_extensions = self.normalize_scan_image_extensions(
            extensions
        )

        if not normalized_extensions:
            normalized_extensions = list(
                self.DEFAULT_SCAN_IMAGE_EXTENSIONS
            )

        return self.set_setting(
            self.SCAN_IMAGE_EXTENSIONS_KEY,
            ",".join(normalized_extensions),
        )

    def reset_scan_image_extensions(self):
        return self.set_scan_image_extensions(
            self.DEFAULT_SCAN_IMAGE_EXTENSIONS
        )

    def normalize_scan_image_extensions(
        self,
        extensions,
    ) -> list[str]:
        if extensions is None:
            return []

        if isinstance(extensions, str):
            raw_extensions = extensions.replace(";", ",").split(",")
        else:
            raw_extensions = list(extensions)

        normalized_extensions = []

        for extension in raw_extensions:
            extension = str(extension or "").strip().lower()

            if not extension:
                continue

            if extension.startswith("."):
                extension = extension[1:]

            extension = "".join(
                character
                for character in extension
                if character.isalnum()
            )

            if not extension:
                continue

            if extension in normalized_extensions:
                continue

            normalized_extensions.append(extension)

        return normalized_extensions

    def get_scan_image_extension_set(self) -> set[str]:
        return {
            f".{extension}"
            for extension in self.get_scan_image_extensions()
        }

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

    def normalize_setting_value(
        self,
        key: str,
        value: Any,
    ) -> str:
        if key == self.SCAN_IMAGE_EXTENSIONS_KEY:
            extensions = self.normalize_scan_image_extensions(value)

            if not extensions:
                extensions = list(self.DEFAULT_SCAN_IMAGE_EXTENSIONS)

            return ",".join(extensions)

        if key in self.INT_SETTING_RULES:
            rule = self.INT_SETTING_RULES[key]
            parsed_value = self.parse_int(
                value,
                default=rule["default"],
            )
            parsed_value = self.clamp_int(
                value=parsed_value,
                minimum=rule["minimum"],
                maximum=rule["maximum"],
            )

            return str(parsed_value)

        if key in self.BOOL_SETTING_KEYS:
            return "true" if self.parse_bool(value) else "false"

        return str(value)

    def parse_int(
        self,
        value,
        default: int,
    ) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def clamp_int(
        self,
        value: int,
        minimum: int,
        maximum: int,
    ) -> int:
        return max(
            minimum,
            min(maximum, value),
        )

    def parse_bool(
        self,
        value,
    ) -> bool:
        return str(value).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

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
