from app.database.connection import get_connection


def initialize_database() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                artist_name TEXT NOT NULL,
                pixiv_id TEXT NOT NULL UNIQUE,

                folder_path TEXT NOT NULL,
                folder_size_bytes INTEGER NOT NULL DEFAULT 0,
                folder_file_count INTEGER NOT NULL DEFAULT 0,
                folder_artwork_count INTEGER NOT NULL DEFAULT 0,

                rating INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'normal',

                memo TEXT NOT NULL DEFAULT '',

                local_latest_artwork_ids TEXT NOT NULL DEFAULT '',
                pixiv_latest_artwork_ids TEXT NOT NULL DEFAULT '',

                update_status TEXT NOT NULL DEFAULT 'unknown',

                last_checked_at TEXT,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        conn.commit()
