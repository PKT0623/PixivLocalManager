from dataclasses import dataclass


@dataclass
class DatabaseBackupInfo:
    file_name: str
    file_path: str
    created_at: str
    size_bytes: int
    size_label: str
    backup_type: str
