SCAN_IMAGE_EXTENSIONS_KEY = "scan_image_extensions"

DEFAULT_SCAN_IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "bmp",
]

PRESERVED_SETTING_KEYS_ON_RESET = {
    "pixiv_phpsessid",
    "pixiv_root_folder",
    "scan_root_folder",
    "last_scan_result",
    "recent_scan_history",
    "last_backup_at",
    "window_width",
    "window_height",
    "window_x",
    "window_y",
    "window_maximized",
}

INT_SETTING_RULES = {
    "pixiv_request_interval_ms": {
        "default": 2000,
        "minimum": 2000,
        "maximum": 600000,
    },
    "pixiv_batch_size": {
        "default": 1000,
        "minimum": 1,
        "maximum": 10000,
    },
    "pixiv_batch_rest_ms": {
        "default": 300000,
        "minimum": 0,
        "maximum": 3600000,
    },
    "pixiv_retry_count": {
        "default": 3,
        "minimum": 0,
        "maximum": 20,
    },
    "update_check_request_interval_ms": {
        "default": 1000,
        "minimum": 0,
        "maximum": 600000,
    },
    "update_check_batch_size": {
        "default": 100,
        "minimum": 1,
        "maximum": 1000,
    },
    "update_check_batch_rest_ms": {
        "default": 180000,
        "minimum": 0,
        "maximum": 3600000,
    },
    "auto_backup_interval_days": {
        "default": 7,
        "minimum": 1,
        "maximum": 365,
    },
    "auto_backup_keep_count": {
        "default": 10,
        "minimum": 1,
        "maximum": 999,
    },
    "window_width": {
        "default": 1500,
        "minimum": 800,
        "maximum": 10000,
    },
    "window_height": {
        "default": 900,
        "minimum": 600,
        "maximum": 10000,
    },
    "window_x": {
        "default": 0,
        "minimum": -10000,
        "maximum": 10000,
    },
    "window_y": {
        "default": 0,
        "minimum": -10000,
        "maximum": 10000,
    },
    "pixiv_manager_page_size": {
        "default": 50,
        "minimum": 10,
        "maximum": 5000,
    },
}

BOOL_SETTING_KEYS = {
    "auto_backup_enabled",
    "auto_rescan",
    "window_maximized",
}
