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

CREATE_FOLLOW_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS follow_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    pixiv_user_id TEXT NOT NULL UNIQUE,
    user_name TEXT NOT NULL DEFAULT '',

    profile_image_url TEXT NOT NULL DEFAULT '',
    comment TEXT NOT NULL DEFAULT '',

    artwork_count INTEGER NOT NULL DEFAULT 0,
    file_count INTEGER NOT NULL DEFAULT 0,

    pixiv_tags TEXT NOT NULL DEFAULT '',

    local_artist_id INTEGER,
    is_local_artist INTEGER NOT NULL DEFAULT 0,

    is_favorite INTEGER NOT NULL DEFAULT 0,
    is_hidden INTEGER NOT NULL DEFAULT 0,

    memo TEXT NOT NULL DEFAULT '',

    source_type TEXT NOT NULL DEFAULT 'manual',

    last_synced_at TEXT,
    sync_status TEXT NOT NULL DEFAULT 'pending',
    sync_error_message TEXT NOT NULL DEFAULT '',
    sync_retry_count INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_FOLLOW_USERS_PIXIV_ID_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_follow_users_pixiv_user_id
ON follow_users (pixiv_user_id)
"""

CREATE_FOLLOW_USERS_LOCAL_ARTIST_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_follow_users_local_artist_id
ON follow_users (local_artist_id)
"""

CREATE_BOOKMARK_ARTWORKS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS bookmark_artworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    artwork_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL DEFAULT '',

    artist_id TEXT NOT NULL DEFAULT '',
    artist_name TEXT NOT NULL DEFAULT '',

    bookmark_count INTEGER NOT NULL DEFAULT 0,
    page_count INTEGER NOT NULL DEFAULT 0,

    ai_type INTEGER NOT NULL DEFAULT 0,
    is_ai_generated INTEGER NOT NULL DEFAULT 0,

    pixiv_tags TEXT NOT NULL DEFAULT '',

    local_artist_id INTEGER,
    is_local_artist INTEGER NOT NULL DEFAULT 0,

    is_favorite INTEGER NOT NULL DEFAULT 0,
    is_hidden INTEGER NOT NULL DEFAULT 0,

    memo TEXT NOT NULL DEFAULT '',

    source_type TEXT NOT NULL DEFAULT 'manual',

    last_synced_at TEXT,
    sync_status TEXT NOT NULL DEFAULT 'pending',
    sync_error_message TEXT NOT NULL DEFAULT '',
    sync_retry_count INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_BOOKMARK_ARTWORKS_ARTWORK_ID_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_bookmark_artworks_artwork_id
ON bookmark_artworks (artwork_id)
"""

CREATE_BOOKMARK_ARTWORKS_ARTIST_ID_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_bookmark_artworks_artist_id
ON bookmark_artworks (artist_id)
"""

CREATE_BOOKMARK_ARTWORKS_LOCAL_ARTIST_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_bookmark_artworks_local_artist_id
ON bookmark_artworks (local_artist_id)
"""

CREATE_ARTIST_UPDATE_HISTORY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS artist_update_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    artist_id INTEGER NOT NULL,
    artist_name TEXT NOT NULL DEFAULT '',
    pixiv_id TEXT NOT NULL DEFAULT '',

    checked_at TEXT NOT NULL,

    action TEXT NOT NULL DEFAULT 'checked',
    result_status TEXT NOT NULL DEFAULT 'unknown',
    result_label TEXT NOT NULL DEFAULT '',

    local_count INTEGER NOT NULL DEFAULT 0,
    pixiv_count INTEGER NOT NULL DEFAULT 0,
    missing_count INTEGER NOT NULL DEFAULT 0,

    missing_ids TEXT NOT NULL DEFAULT '',
    download_candidate_ids TEXT NOT NULL DEFAULT '',

    error_message TEXT NOT NULL DEFAULT '',
    error_reason TEXT NOT NULL DEFAULT '',

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_ARTIST_UPDATE_HISTORY_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_artist_update_history_artist_id
ON artist_update_history (artist_id)
"""

CREATE_ARTIST_UPDATE_HISTORY_CHECKED_AT_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_artist_update_history_checked_at
ON artist_update_history (checked_at)
"""

CREATE_APP_SETTINGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
"""
