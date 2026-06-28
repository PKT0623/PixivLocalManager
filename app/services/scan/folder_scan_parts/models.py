from dataclasses import dataclass, field


@dataclass
class FolderScanResult:
    artist_name: str
    pixiv_id: str
    folder_path: str
    folder_size_bytes: int
    folder_file_count: int
    folder_artwork_count: int
    local_latest_artwork_ids: str
    extension_counts: dict[str, int] = field(default_factory=dict)
    invalid_artwork_file_names: list[str] = field(default_factory=list)
    non_artwork_files: list[dict] = field(default_factory=list)
    non_artwork_summary: dict = field(default_factory=dict)
    non_artwork_summary_text: str = "비작품 파일 없음"
