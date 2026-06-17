import json
from datetime import datetime
from pathlib import Path

from app.database.app_setting_repository import AppSettingRepository
from app.database.connection import DATA_DIR


class SettingsBackupService:
    BACKUP_DIR = DATA_DIR / "backups" / "settings"

    def __init__(self):
        self.repo = AppSettingRepository()

    def export_settings(
        self,
        file_path: str,
    ) -> str:
        settings = self.repo.get_all()

        backup_data = {
            "backup_type": "app_settings",
            "created_at": datetime.now().isoformat(),
            "setting_count": len(settings),
            "settings": [
                {
                    "key": setting.key,
                    "value": setting.value,
                }
                for setting in settings
            ],
        }

        path = Path(file_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as backup_file:
            json.dump(
                backup_data,
                backup_file,
                ensure_ascii=False,
                indent=4,
            )

        return str(path)

    def import_settings(
        self,
        file_path: str,
    ) -> dict:
        path = Path(file_path)

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as backup_file:
            data = json.load(backup_file)

        if not isinstance(data, dict):
            raise ValueError("설정 백업 파일 형식이 올바르지 않습니다.")

        if data.get("backup_type") != "app_settings":
            raise ValueError("설정 백업 파일이 아닙니다.")

        settings = data.get("settings", [])

        if not isinstance(settings, list):
            raise ValueError("설정 데이터 형식이 올바르지 않습니다.")

        imported_count = 0
        skipped_count = 0

        for setting in settings:
            if not isinstance(setting, dict):
                skipped_count += 1
                continue

            key = str(setting.get("key", "") or "").strip()
            value = setting.get("value")

            if not key or value is None:
                skipped_count += 1
                continue

            self.repo.set(
                key,
                str(value),
            )
            imported_count += 1

        return {
            "imported_count": imported_count,
            "skipped_count": skipped_count,
        }

    def get_default_backup_dir(self) -> Path:
        self.BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        return self.BACKUP_DIR
