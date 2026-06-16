CREATE_ARTISTS_TABLE_SQL = """
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

CREATE_APP_SETTINGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
"""
