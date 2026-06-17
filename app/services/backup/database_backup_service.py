import shutil
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from app.database.app_setting_repository import AppSettingRepository
from app.database.connection import DATA_DIR, DB_PATH


@dataclass
class DatabaseBackupInfo:
    file_name: str
    file_path: str
    created_at: str
    size_bytes: int
    size_label: str
    backup_type: str


class DatabaseBackupService:
    BACKUP_DIR = DATA_DIR / "backups" / "database"

    AUTO_BACKUP_ENABLED_KEY = "auto_backup_enabled"
    AUTO_BACKUP_INTERVAL_DAYS_KEY = "auto_backup_interval_days"
    AUTO_BACKUP_KEEP_COUNT_KEY = "auto_backup_keep_count"
    LAST_BACKUP_AT_KEY = "last_backup_at"

    DEFAULT_INTERVAL_DAYS = 7
    DEFAULT_KEEP_COUNT = 10

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

    def is_auto_backup_enabled(self) -> bool:
        setting = self.settings_repo.get(self.AUTO_BACKUP_ENABLED_KEY)

        if setting is None:
            return False

        return str(setting.value).lower() in {
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
        )

    def get_auto_backup_keep_count(self) -> int:
        return self._get_int_setting(
            self.AUTO_BACKUP_KEEP_COUNT_KEY,
            self.DEFAULT_KEEP_COUNT,
            minimum=1,
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
        self.settings_repo.set(
            self.AUTO_BACKUP_ENABLED_KEY,
            "true" if enabled else "false",
        )
        self.settings_repo.set(
            self.AUTO_BACKUP_INTERVAL_DAYS_KEY,
            str(max(1, int(interval_days))),
        )
        self.settings_repo.set(
            self.AUTO_BACKUP_KEEP_COUNT_KEY,
            str(max(1, int(keep_count))),
        )

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
        backup_path = self.BACKUP_DIR / (
            f"pixiv_manager_{backup_type}_{timestamp}.db"
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
        backup_path = self.BACKUP_DIR / (
            f"pixiv_manager_before_restore_{timestamp}.db"
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

        if not self.is_valid_sqlite_database(source_path):
            raise ValueError("유효한 SQLite DB 백업 파일이 아닙니다.")

        if DB_PATH.exists() and self.is_valid_sqlite_database(DB_PATH):
            self.create_restore_safety_backup()

        shutil.copy2(
            source_path,
            DB_PATH,
        )

    def delete_database_backup(
        self,
        backup_path: str,
    ) -> None:
        path = Path(backup_path)

        if not path.exists():
            return

        if not path.is_file():
            return

        backup_dir = self.BACKUP_DIR.resolve()
        target_path = path.resolve()

        if backup_dir not in target_path.parents:
            raise ValueError("백업 폴더 밖의 파일은 삭제할 수 없습니다.")

        self._delete_file_with_retry(path)

    def list_database_backups(self) -> list[DatabaseBackupInfo]:
        self.BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup_files = sorted(
            self.BACKUP_DIR.glob("*.db"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        return [
            self._build_backup_info(path)
            for path in backup_files
            if path.is_file()
        ]

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

    def get_backup_total_size_bytes(self) -> int:
        return sum(
            backup.size_bytes
            for backup in self.list_database_backups()
        )

    def get_backup_total_size_label(self) -> str:
        return self.format_bytes(
            self.get_backup_total_size_bytes()
        )

    def is_valid_sqlite_database(
        self,
        file_path: Path,
    ) -> bool:
        try:
            with open(
                file_path,
                "rb",
            ) as db_file:
                header = db_file.read(16)

            if not header.startswith(b"SQLite format 3"):
                return False

            with sqlite3.connect(file_path) as conn:
                result = conn.execute(
                    "PRAGMA integrity_check"
                ).fetchone()

            return result is not None and result[0] == "ok"
        except (OSError, sqlite3.DatabaseError):
            return False

    def _delete_file_with_retry(
        self,
        path: Path,
    ) -> None:
        last_error = None

        for _ in range(8):
            try:
                path.unlink()
                return
            except PermissionError as error:
                last_error = error
                time.sleep(0.25)

        if last_error is not None:
            raise last_error

    def _build_backup_info(
        self,
        path: Path,
    ) -> DatabaseBackupInfo:
        stat = path.stat()
        created_at = datetime.fromtimestamp(stat.st_mtime)

        return DatabaseBackupInfo(
            file_name=path.name,
            file_path=str(path),
            created_at=created_at.strftime("%Y-%m-%d %H:%M:%S"),
            size_bytes=stat.st_size,
            size_label=self.format_bytes(stat.st_size),
            backup_type=self._detect_backup_type(path.name),
        )

    def _detect_backup_type(
        self,
        file_name: str,
    ) -> str:
        if "_auto_" in file_name:
            return "auto"

        if "_manual_" in file_name:
            return "manual"

        if "_before_restore_" in file_name:
            return "restore_safety"

        return "unknown"

    def _get_int_setting(
        self,
        key: str,
        default: int,
        minimum: int = 0,
    ) -> int:
        setting = self.settings_repo.get(key)

        if setting is None:
            return default

        try:
            value = int(setting.value)
        except (TypeError, ValueError):
            return default

        return max(minimum, value)

    def format_bytes(
        self,
        size_bytes: int,
    ) -> str:
        size = float(size_bytes)

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size:.1f} PB"
