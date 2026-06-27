import sqlite3
from pathlib import Path


USER_DATA_DIR = Path.home() / "PixivLocalManager_Data"
DATA_DIR = USER_DATA_DIR / "data"
BACKUPS_DIR = USER_DATA_DIR / "backups"
EXPORTS_DIR = USER_DATA_DIR / "exports"
THUMBNAILS_DIR = USER_DATA_DIR / "thumbnails"
LOGS_DIR = USER_DATA_DIR / "logs"

DB_PATH = DATA_DIR / "pixiv_manager.db"


def ensure_user_data_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_user_data_dirs()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn
