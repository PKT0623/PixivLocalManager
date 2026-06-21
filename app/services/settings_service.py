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

    def get_bool_setting(
        self,
        key: str,
        default: bool = False,
    ) -> bool:
        value = self.get_setting(key)

        if value is None:
            return default

        return str(value).lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

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
        return self.repo.set(key, str(value))

    def delete_setting(
        self,
        key: str,
    ):
        return self.repo.delete(key)

    def reset_to_default(self):
        self.repo.delete_all()

        default_settings = {
            "scan_interval": 60,
            "auto_rescan": True,
            "theme": "light",
            "pixiv_request_interval_ms": 2000,
            "pixiv_batch_size": 1000,
            "pixiv_batch_rest_ms": 300000,
            "pixiv_retry_count": 3,
            "update_check_request_interval_ms": 1000,
            "update_check_batch_size": 20,
            "update_check_batch_rest_ms": 180000,
            "auto_backup_enabled": False,
            "auto_backup_interval_days": 7,
            "auto_backup_keep_count": 10,
            self.SCAN_IMAGE_EXTENSIONS_KEY: ",".join(
                self.DEFAULT_SCAN_IMAGE_EXTENSIONS
            ),
        }

        for key, value in default_settings.items():
            self.repo.set(key, value)

        return self.repo.get_all()
