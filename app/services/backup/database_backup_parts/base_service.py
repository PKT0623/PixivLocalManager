import shutil
from datetime import datetime
from pathlib import Path

from app.database.app_setting_repository import AppSettingRepository
from app.database.connection import DB_PATH

from .constants import BACKUP_DIR
from .file_utils import DatabaseBackupFileUtilsMixin
from .info_mixin import DatabaseBackupInfoMixin
from .settings_mixin import DatabaseBackupSettingsMixin


class DatabaseBackupService(
    DatabaseBackupSettingsMixin,
    DatabaseBackupInfoMixin,
    DatabaseBackupFileUtilsMixin,
):
    BACKUP_DIR = BACKUP_DIR

    def __init__(self):
        self.settings_repo = AppSettingRepository()

    def run_startup_auto_backup(self) -> str | None:
        if not self.is_auto_backup_enabled():
            return None

        if not self.should_create_auto_backup():
            return None

        backup_path = self.create_database_backup(
            backup_type="auto",
        )
        self.prune_old_backups()
        return backup_path

    def create_database_backup(
        self,
        backup_type: str = "manual",
    ) -> str:
        if not DB_PATH.exists():
            raise FileNotFoundError("백업할 DB 파일을 찾을 수 없습니다.")

        if not self.is_valid_sqlite_database(DB_PATH):
            raise ValueError("현재 DB 파일이 유효한 SQLite DB가 아닙니다.")

        self.BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._get_unique_backup_path(
            backup_type=backup_type,
            timestamp=timestamp,
        )

        shutil.copy2(
            DB_PATH,
            backup_path,
        )

        self.settings_repo.set(
            self.LAST_BACKUP_AT_KEY,
            datetime.now().isoformat(),
        )

        return str(backup_path)

    def create_restore_safety_backup(self) -> str:
        if not DB_PATH.exists():
            raise FileNotFoundError("안전 백업할 DB 파일을 찾을 수 없습니다.")

        self.BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._get_unique_backup_path(
            backup_type="before_restore",
            timestamp=timestamp,
        )

        shutil.copy2(
            DB_PATH,
            backup_path,
        )

        return str(backup_path)

    def restore_database_backup(
        self,
        backup_path: str,
    ) -> None:
        source_path = Path(backup_path)

        if not source_path.exists():
            raise FileNotFoundError("복원할 백업 파일을 찾을 수 없습니다.")

        if not source_path.is_file():
            raise ValueError("복원할 백업 파일 경로가 올바르지 않습니다.")

        if source_path.resolve() == DB_PATH.resolve():
            raise ValueError("현재 사용 중인 DB 파일은 복원 대상으로 사용할 수 없습니다.")

        if not self.is_valid_sqlite_database(source_path):
            raise ValueError("유효한 SQLite DB 백업 파일이 아닙니다.")

        if DB_PATH.exists() and self.is_valid_sqlite_database(DB_PATH):
            self.create_restore_safety_backup()

        DB_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source_path,
            DB_PATH,
        )
        self._release_file_handles()

    def delete_database_backup(
        self,
        backup_path: str,
    ) -> None:
        path = Path(backup_path)

        if not path.exists():
            return

        if not path.is_file():
            return

        self.validate_backup_delete_target(path)

        self._release_file_handles()
        self._delete_file_with_retry(path)

    def prune_old_backups(self) -> list[str]:
        keep_count = self.get_auto_backup_keep_count()
        backups = [
            backup
            for backup in self.list_database_backups()
            if backup.backup_type in {"auto", "manual"}
        ]

        if len(backups) <= keep_count:
            return []

        deleted_paths = []

        for backup in backups[keep_count:]:
            self.delete_database_backup(backup.file_path)
            deleted_paths.append(backup.file_path)

        return deleted_paths
