from pathlib import Path

from app.services.settings_service import SettingsService

from .folder_scan_parts import (
    ArtworkExtractorMixin,
    FileScannerMixin,
    FolderNameMixin,
    FolderScanResult,
)
from .non_artwork_file_collector import NonArtworkFileCollector


class FolderScanService(
    FolderNameMixin,
    FileScannerMixin,
    ArtworkExtractorMixin,
):
    def __init__(self):
        self.settings_service = SettingsService()
        self.non_artwork_collector = NonArtworkFileCollector()

    @property
    def image_extensions(self) -> set[str]:
        return self.settings_service.get_scan_image_extension_set()

    def scan_folder(self, folder_path: str) -> FolderScanResult:
        path = Path(folder_path)

        if not path.exists():
            raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")

        if not path.is_dir():
            raise NotADirectoryError(f"폴더 경로가 아닙니다: {folder_path}")

        artist_name, pixiv_id = self.parse_artist_folder_name(path.name)
        scan_data = self._scan_folder_files(path)
        artwork_result = self._extract_artwork_ids(
            folder_path=path,
            image_files=scan_data["image_files"],
            non_artwork_files=scan_data["non_artwork_files"],
        )
        non_artwork_files = artwork_result["non_artwork_files"]
        non_artwork_summary = self.non_artwork_collector.summarize(
            non_artwork_files
        )

        return FolderScanResult(
            artist_name=artist_name,
            pixiv_id=pixiv_id,
            folder_path=str(path),
            folder_size_bytes=scan_data["folder_size_bytes"],
            folder_file_count=len(scan_data["image_files"]),
            folder_artwork_count=len(artwork_result["artwork_ids"]),
            local_latest_artwork_ids=",".join(artwork_result["artwork_ids"]),
            extension_counts=scan_data["extension_counts"],
            invalid_artwork_file_names=artwork_result["invalid_file_names"],
            non_artwork_files=non_artwork_files,
            non_artwork_summary=non_artwork_summary,
            non_artwork_summary_text=(
                self.non_artwork_collector.format_summary_text(
                    non_artwork_summary
                )
            ),
        )
