from app.database.connection import DATA_DIR


BACKUP_DIR = DATA_DIR / "backups" / "database"

AUTO_BACKUP_ENABLED_KEY = "auto_backup_enabled"
AUTO_BACKUP_INTERVAL_DAYS_KEY = "auto_backup_interval_days"
AUTO_BACKUP_KEEP_COUNT_KEY = "auto_backup_keep_count"
LAST_BACKUP_AT_KEY = "last_backup_at"

DEFAULT_INTERVAL_DAYS = 7
DEFAULT_KEEP_COUNT = 10
MAX_INTERVAL_DAYS = 365
MAX_KEEP_COUNT = 999

DELETE_RETRY_COUNT = 40
DELETE_RETRY_INTERVAL_SECONDS = 0.25
