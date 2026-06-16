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


def run_migrations(cursor) -> None:
    _ensure_artist_columns(cursor)


def _ensure_artist_columns(cursor) -> None:
    existing_columns = _get_table_columns(cursor, "artists")

    for column_name, query in ARTIST_COLUMN_MIGRATIONS.items():
        if column_name not in existing_columns:
            cursor.execute(query)


def _get_table_columns(cursor, table_name: str) -> set[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()

    return {
        row[1]
        for row in rows
    }
