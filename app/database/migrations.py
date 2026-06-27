from app.database.table_definitions import (
    CREATE_ARTIST_UPDATE_HISTORY_CHECKED_AT_INDEX_SQL,
    CREATE_ARTIST_UPDATE_HISTORY_INDEX_SQL,
    CREATE_ARTIST_UPDATE_HISTORY_TABLE_SQL,
    CREATE_BOOKMARK_ARTWORKS_ARTIST_ID_INDEX_SQL,
    CREATE_BOOKMARK_ARTWORKS_ARTWORK_ID_INDEX_SQL,
    CREATE_BOOKMARK_ARTWORKS_LOCAL_ARTIST_INDEX_SQL,
    CREATE_BOOKMARK_ARTWORKS_TABLE_SQL,
    CREATE_FOLLOW_USERS_LOCAL_ARTIST_INDEX_SQL,
    CREATE_FOLLOW_USERS_PIXIV_ID_INDEX_SQL,
    CREATE_FOLLOW_USERS_TABLE_SQL,
)


ARTIST_COLUMN_MIGRATIONS = {
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


FOLLOW_USER_COLUMN_MIGRATIONS = {
    "file_count": (
        "ALTER TABLE follow_users "
        "ADD COLUMN file_count INTEGER NOT NULL DEFAULT 0"
    ),
    "sync_status": (
        "ALTER TABLE follow_users "
        "ADD COLUMN sync_status TEXT NOT NULL DEFAULT 'pending'"
    ),
    "sync_error_message": (
        "ALTER TABLE follow_users "
        "ADD COLUMN sync_error_message TEXT NOT NULL DEFAULT ''"
    ),
    "sync_retry_count": (
        "ALTER TABLE follow_users "
        "ADD COLUMN sync_retry_count INTEGER NOT NULL DEFAULT 0"
    ),
}


BOOKMARK_ARTWORK_COLUMN_MIGRATIONS = {
    "ai_type": (
        "ALTER TABLE bookmark_artworks "
        "ADD COLUMN ai_type INTEGER NOT NULL DEFAULT 0"
    ),
    "is_ai_generated": (
        "ALTER TABLE bookmark_artworks "
        "ADD COLUMN is_ai_generated INTEGER NOT NULL DEFAULT 0"
    ),
    "sync_status": (
        "ALTER TABLE bookmark_artworks "
        "ADD COLUMN sync_status TEXT NOT NULL DEFAULT 'pending'"
    ),
    "sync_error_message": (
        "ALTER TABLE bookmark_artworks "
        "ADD COLUMN sync_error_message TEXT NOT NULL DEFAULT ''"
    ),
    "sync_retry_count": (
        "ALTER TABLE bookmark_artworks "
        "ADD COLUMN sync_retry_count INTEGER NOT NULL DEFAULT 0"
    ),
}


def run_migrations(cursor) -> None:
    _ensure_artist_columns(cursor)
    _ensure_artist_update_history_table(cursor)
    _ensure_follow_users_table(cursor)
    _ensure_follow_user_columns(cursor)
    _ensure_bookmark_artworks_table(cursor)
    _ensure_bookmark_artwork_columns(cursor)


def _ensure_artist_columns(cursor) -> None:
    existing_columns = _get_table_columns(cursor, "artists")

    for column_name, query in ARTIST_COLUMN_MIGRATIONS.items():
        if column_name not in existing_columns:
            cursor.execute(query)


def _ensure_artist_update_history_table(cursor) -> None:
    cursor.execute(CREATE_ARTIST_UPDATE_HISTORY_TABLE_SQL)
    cursor.execute(CREATE_ARTIST_UPDATE_HISTORY_INDEX_SQL)
    cursor.execute(CREATE_ARTIST_UPDATE_HISTORY_CHECKED_AT_INDEX_SQL)


def _ensure_follow_users_table(cursor) -> None:
    cursor.execute(CREATE_FOLLOW_USERS_TABLE_SQL)
    cursor.execute(CREATE_FOLLOW_USERS_PIXIV_ID_INDEX_SQL)
    cursor.execute(CREATE_FOLLOW_USERS_LOCAL_ARTIST_INDEX_SQL)


def _ensure_follow_user_columns(cursor) -> None:
    existing_columns = _get_table_columns(cursor, "follow_users")

    for column_name, query in FOLLOW_USER_COLUMN_MIGRATIONS.items():
        if column_name not in existing_columns:
            cursor.execute(query)


def _ensure_bookmark_artworks_table(cursor) -> None:
    cursor.execute(CREATE_BOOKMARK_ARTWORKS_TABLE_SQL)
    cursor.execute(CREATE_BOOKMARK_ARTWORKS_ARTWORK_ID_INDEX_SQL)
    cursor.execute(CREATE_BOOKMARK_ARTWORKS_ARTIST_ID_INDEX_SQL)
    cursor.execute(CREATE_BOOKMARK_ARTWORKS_LOCAL_ARTIST_INDEX_SQL)


def _ensure_bookmark_artwork_columns(cursor) -> None:
    existing_columns = _get_table_columns(cursor, "bookmark_artworks")

    for column_name, query in BOOKMARK_ARTWORK_COLUMN_MIGRATIONS.items():
        if column_name not in existing_columns:
            cursor.execute(query)


def _get_table_columns(cursor, table_name: str) -> set[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()

    return {
        row[1]
        for row in rows
    }
