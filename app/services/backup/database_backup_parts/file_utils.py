import gc
import sqlite3
import time
from pathlib import Path

from app.database.connection import DB_PATH

from .constants import (
    DELETE_RETRY_COUNT,
    DELETE_RETRY_INTERVAL_SECONDS,
)


class DatabaseBackupFileUtilsMixin:
    DELETE_RETRY_COUNT = DELETE_RETRY_COUNT
    DELETE_RETRY_INTERVAL_SECONDS = DELETE_RETRY_INTERVAL_SECONDS

    def is_valid_sqlite_database(
        self,
        file_path: Path,
    ) -> bool:
        conn = None

        try:
            with open(
                file_path,
                "rb",
            ) as db_file:
                header = db_file.read(16)

            if not header.startswith(b"SQLite format 3"):
                return False

            conn = sqlite3.connect(
                f"file:{file_path.as_posix()}?mode=ro&immutable=1",
                uri=True,
                timeout=1,
            )
            result = conn.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            return result is not None and result[0] == "ok"
        except (OSError, sqlite3.DatabaseError):
            return False
        finally:
            if conn is not None:
                conn.close()

            self._release_file_handles()

    def _delete_file_with_retry(
        self,
        path: Path,
    ) -> None:
        last_error = None

        for _ in range(self.DELETE_RETRY_COUNT):
            try:
                path.unlink()
                return
            except PermissionError as error:
                last_error = error
                self._release_file_handles()
                time.sleep(self.DELETE_RETRY_INTERVAL_SECONDS)
            except OSError as error:
                if getattr(error, "winerror", None) != 32:
                    raise

                last_error = error
                self._release_file_handles()
                time.sleep(self.DELETE_RETRY_INTERVAL_SECONDS)

        if last_error is not None:
            raise last_error

    def _release_file_handles(self):
        gc.collect()
        time.sleep(0.05)

    def _get_unique_backup_path(
        self,
        backup_type: str,
        timestamp: str,
    ) -> Path:
        backup_path = self.BACKUP_DIR / (
            f"pixiv_manager_{backup_type}_{timestamp}.db"
        )

        if not backup_path.exists():
            return backup_path

        for index in range(1, 1000):
            candidate_path = self.BACKUP_DIR / (
                f"pixiv_manager_{backup_type}_{timestamp}_{index}.db"
            )

            if not candidate_path.exists():
                return candidate_path

        raise FileExistsError("사용 가능한 백업 파일명을 생성하지 못했습니다.")

    def validate_backup_delete_target(
        self,
        path: Path,
    ) -> None:
        backup_dir = self.BACKUP_DIR.resolve()
        target_path = path.resolve()

        if target_path == DB_PATH.resolve():
            raise ValueError("현재 사용 중인 DB 파일은 삭제할 수 없습니다.")

        if backup_dir not in target_path.parents:
            raise ValueError("백업 폴더 밖의 파일은 삭제할 수 없습니다.")
