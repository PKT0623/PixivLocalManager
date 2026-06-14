import csv
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from app.database.connection import DB_PATH


def get_database_path() -> Path:
    return DB_PATH


def is_valid_sqlite_database(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as db_file:
            header = db_file.read(16)

        if not header.startswith(b"SQLite format 3"):
            return False

        with sqlite3.connect(file_path) as conn:
            result = conn.execute("PRAGMA integrity_check").fetchone()

        return result is not None and result[0] == "ok"
    except (OSError, sqlite3.DatabaseError):
        return False


def create_database_backup(db_path: Path, backup_folder: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(backup_folder) / f"pixiv_manager_backup_{timestamp}.db"

    shutil.copy2(db_path, backup_path)

    return backup_path


def create_restore_safety_backup(db_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_backup_path = db_path.parent / f"pixiv_manager_before_restore_{timestamp}.db"

    shutil.copy2(db_path, safe_backup_path)

    return safe_backup_path


def restore_database(restore_path: Path, db_path: Path):
    shutil.copy2(restore_path, db_path)


def export_artists_to_csv(export_file: str, artists: list[dict]):
    fieldnames = [
        "id",
        "artist_name",
        "pixiv_id",
        "folder_path",
        "folder_artwork_count",
        "folder_file_count",
        "rating",
        "status",
        "update_status",
        "memo",
        "created_at",
        "updated_at",
    ]

    with open(
        export_file,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(artists)
