from datetime import datetime
from pathlib import Path

from .models import DatabaseBackupInfo


class DatabaseBackupInfoMixin:
    def list_database_backups(self) -> list[DatabaseBackupInfo]:
        self.BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup_infos = []

        for path in self.BACKUP_DIR.glob("*.db"):
            if not path.is_file():
                continue

            backup_info = self._try_build_backup_info(path)

            if backup_info is None:
                continue

            backup_infos.append(backup_info)

        return sorted(
            backup_infos,
            key=lambda backup: backup.created_at,
            reverse=True,
        )

    def get_backup_total_size_bytes(self) -> int:
        return sum(
            backup.size_bytes
            for backup in self.list_database_backups()
        )

    def get_backup_total_size_label(self) -> str:
        return self.format_bytes(
            self.get_backup_total_size_bytes()
        )

    def _try_build_backup_info(
        self,
        path: Path,
    ) -> DatabaseBackupInfo | None:
        try:
            return self._build_backup_info(path)
        except OSError:
            return None

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
