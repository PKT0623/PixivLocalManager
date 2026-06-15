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

                is_favorite INTEGER NOT NULL DEFAULT 0,
                is_hidden INTEGER NOT NULL DEFAULT 0,
                artist_tags TEXT NOT NULL DEFAULT '',

                memo TEXT NOT NULL DEFAULT '',
                reference_links TEXT NOT NULL DEFAULT '',
                download_note TEXT NOT NULL DEFAULT '',

                local_latest_artwork_ids TEXT NOT NULL DEFAULT '',
                pixiv_latest_artwork_ids TEXT NOT NULL DEFAULT '',

                update_status TEXT NOT NULL DEFAULT 'unknown',

                last_checked_at TEXT,
                last_viewed_at TEXT,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        _ensure_artist_columns(cursor)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        conn.commit()


def _ensure_artist_columns(cursor) -> None:
    existing_columns = _get_table_columns(cursor, "artists")

    migrations = {
        "is_favorite": (
            "ALTER TABLE artists "
            "ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0"
        ),
        "is_hidden": (
            "ALTER TABLE artists "
            "ADD COLUMN is_hidden INTEGER NOT NULL DEFAULT 0"
        ),
        "artist_tags": (
            "ALTER TABLE artists "
            "ADD COLUMN artist_tags TEXT NOT NULL DEFAULT ''"
        ),
        "reference_links": (
            "ALTER TABLE artists "
            "ADD COLUMN reference_links TEXT NOT NULL DEFAULT ''"
        ),
        "download_note": (
            "ALTER TABLE artists "
            "ADD COLUMN download_note TEXT NOT NULL DEFAULT ''"
        ),
        "last_viewed_at": (
            "ALTER TABLE artists "
            "ADD COLUMN last_viewed_at TEXT"
        ),
    }

    for column_name, query in migrations.items():
        if column_name not in existing_columns:
            cursor.execute(query)


def _get_table_columns(cursor, table_name: str) -> set[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()

    return {
        row[1]
        for row in rows
    }
