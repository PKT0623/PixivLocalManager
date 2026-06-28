from datetime import datetime, timedelta

from .constants import (
    AUTO_BACKUP_ENABLED_KEY,
    AUTO_BACKUP_INTERVAL_DAYS_KEY,
    AUTO_BACKUP_KEEP_COUNT_KEY,
    DEFAULT_INTERVAL_DAYS,
    DEFAULT_KEEP_COUNT,
    LAST_BACKUP_AT_KEY,
    MAX_INTERVAL_DAYS,
    MAX_KEEP_COUNT,
)


class DatabaseBackupSettingsMixin:
    AUTO_BACKUP_ENABLED_KEY = AUTO_BACKUP_ENABLED_KEY
    AUTO_BACKUP_INTERVAL_DAYS_KEY = AUTO_BACKUP_INTERVAL_DAYS_KEY
    AUTO_BACKUP_KEEP_COUNT_KEY = AUTO_BACKUP_KEEP_COUNT_KEY
    LAST_BACKUP_AT_KEY = LAST_BACKUP_AT_KEY

    DEFAULT_INTERVAL_DAYS = DEFAULT_INTERVAL_DAYS
    DEFAULT_KEEP_COUNT = DEFAULT_KEEP_COUNT
    MAX_INTERVAL_DAYS = MAX_INTERVAL_DAYS
    MAX_KEEP_COUNT = MAX_KEEP_COUNT

    def is_auto_backup_enabled(self) -> bool:
        setting = self.settings_repo.get(self.AUTO_BACKUP_ENABLED_KEY)

        if setting is None:
            return False

        return str(setting.value).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    def should_create_auto_backup(self) -> bool:
        interval_days = self.get_auto_backup_interval_days()
        last_backup_at = self.get_last_backup_at()

        if last_backup_at is None:
            return True

        next_backup_at = last_backup_at + timedelta(days=interval_days)

        return datetime.now() >= next_backup_at

    def get_auto_backup_interval_days(self) -> int:
        return self._get_int_setting(
            self.AUTO_BACKUP_INTERVAL_DAYS_KEY,
            self.DEFAULT_INTERVAL_DAYS,
            minimum=1,
            maximum=self.MAX_INTERVAL_DAYS,
        )

    def get_auto_backup_keep_count(self) -> int:
        return self._get_int_setting(
            self.AUTO_BACKUP_KEEP_COUNT_KEY,
            self.DEFAULT_KEEP_COUNT,
            minimum=1,
            maximum=self.MAX_KEEP_COUNT,
        )

    def get_last_backup_at(self) -> datetime | None:
        setting = self.settings_repo.get(self.LAST_BACKUP_AT_KEY)

        if setting is None or not setting.value:
            return None

        try:
            return datetime.fromisoformat(str(setting.value))
        except ValueError:
            return None

    def get_last_backup_at_label(self) -> str:
        last_backup_at = self.get_last_backup_at()

        if last_backup_at is None:
            return "-"

        return last_backup_at.strftime("%Y-%m-%d %H:%M:%S")

    def save_auto_backup_settings(
        self,
        enabled: bool,
        interval_days: int,
        keep_count: int,
    ) -> None:
        normalized_interval_days = self._clamp_int(
            value=interval_days,
            default=self.DEFAULT_INTERVAL_DAYS,
            minimum=1,
            maximum=self.MAX_INTERVAL_DAYS,
        )
        normalized_keep_count = self._clamp_int(
            value=keep_count,
            default=self.DEFAULT_KEEP_COUNT,
            minimum=1,
            maximum=self.MAX_KEEP_COUNT,
        )

        self.settings_repo.set(
            self.AUTO_BACKUP_ENABLED_KEY,
            "true" if enabled else "false",
        )
        self.settings_repo.set(
            self.AUTO_BACKUP_INTERVAL_DAYS_KEY,
            str(normalized_interval_days),
        )
        self.settings_repo.set(
            self.AUTO_BACKUP_KEEP_COUNT_KEY,
            str(normalized_keep_count),
        )

    def _get_int_setting(
        self,
        key: str,
        default: int,
        minimum: int = 0,
        maximum: int = 999999,
    ) -> int:
        setting = self.settings_repo.get(key)

        if setting is None:
            return default

        return self._clamp_int(
            value=setting.value,
            default=default,
            minimum=minimum,
            maximum=maximum,
        )

    def _clamp_int(
        self,
        value,
        default: int,
        minimum: int,
        maximum: int,
    ) -> int:
        try:
            parsed_value = int(value)
        except (TypeError, ValueError):
            parsed_value = default

        return max(
            minimum,
            min(maximum, parsed_value),
        )
