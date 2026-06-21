from dataclasses import dataclass, field
from pathlib import Path
import re

from app.services.settings_service import SettingsService

from .non_artwork_file_collector import NonArtworkFileCollector


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


class FolderScanService:
    BRACKETED_PIXIV_ID_PATTERN = re.compile(r"[\[\(](\d{5,})[\]\)]")
    TRAILING_PIXIV_ID_PATTERN = re.compile(r"[-_ ]+(\d{5,})$")
    ANY_PIXIV_ID_PATTERN = re.compile(r"(\d{5,})")

    PIXIV_ARTWORK_FILE_PATTERN = re.compile(
        r"^(\d{5,})(?:_p\d+)?(?:\D.*)?$"
    )
    ARTWORK_ID_PATTERN = re.compile(r"(\d{5,})")

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

    def parse_artist_folder_name(
        self,
        folder_name: str,
    ) -> tuple[str, str]:
        folder_name = folder_name.strip()

        match = self._find_pixiv_id_match(folder_name)

        if match is None:
            return folder_name, ""

        pixiv_id = match.group(1)

        artist_name = (
            folder_name[: match.start()]
            + folder_name[match.end():]
        )
        artist_name = artist_name.strip(" _-")

        return artist_name.strip(), pixiv_id

    def get_folder_name_rule_status(
        self,
        folder_name: str,
    ) -> dict:
        folder_name = folder_name.strip()

        if not folder_name:
            return {
                "level": "error",
                "message": "폴더명이 비어 있습니다.",
            }

        trailing_match = self.TRAILING_PIXIV_ID_PATTERN.search(folder_name)

        if trailing_match is not None:
            return {
                "level": "ok",
                "message": "권장 폴더명 형식입니다.",
            }

        bracket_matches = list(
            self.BRACKETED_PIXIV_ID_PATTERN.finditer(folder_name)
        )

        if bracket_matches:
            return {
                "level": "ok",
                "message": "권장 폴더명 형식입니다.",
            }

        any_matches = list(
            self.ANY_PIXIV_ID_PATTERN.finditer(folder_name)
        )

        if any_matches:
            return {
                "level": "warning",
                "message": (
                    "Pixiv ID는 찾았지만 폴더명 형식이 애매합니다. "
                    "권장 형식은 '작가명-12345678' 또는 "
                    "'작가명 [12345678]'입니다."
                ),
            }

        return {
            "level": "error",
            "message": "폴더명에서 Pixiv ID를 찾을 수 없습니다.",
        }

    def _find_pixiv_id_match(self, folder_name: str):
        trailing_match = self.TRAILING_PIXIV_ID_PATTERN.search(folder_name)

        if trailing_match is not None:
            return trailing_match

        bracket_matches = list(
            self.BRACKETED_PIXIV_ID_PATTERN.finditer(folder_name)
        )

        if bracket_matches:
            return bracket_matches[-1]

        any_matches = list(
            self.ANY_PIXIV_ID_PATTERN.finditer(folder_name)
        )

        if any_matches:
            return any_matches[-1]

        return None

    def _scan_folder_files(self, folder_path: Path) -> dict:
        image_files: list[Path] = []
        non_artwork_files: list[dict] = []
        folder_size_bytes = 0
        extension_counts: dict[str, int] = {}
        image_extensions = self.image_extensions

        for file_path in folder_path.rglob("*"):
            if not file_path.is_file():
                continue

            try:
                file_size = file_path.stat().st_size
                folder_size_bytes += file_size
            except OSError:
                non_artwork_files.append(
                    self.non_artwork_collector.build_record(
                        file_path=file_path,
                        folder_path=folder_path,
                        reason=(
                            self.non_artwork_collector
                            .REASON_SCAN_ERROR
                        ),
                    )
                )
                continue

            if file_size <= 0:
                non_artwork_files.append(
                    self.non_artwork_collector.build_record(
                        file_path=file_path,
                        folder_path=folder_path,
                        reason=(
                            self.non_artwork_collector
                            .REASON_EMPTY_FILE
                        ),
                        size_bytes=file_size,
                    )
                )
                continue

            if file_path.suffix.lower() not in image_extensions:
                non_artwork_files.append(
                    self.non_artwork_collector.build_record(
                        file_path=file_path,
                        folder_path=folder_path,
                        reason=(
                            self.non_artwork_collector
                            .REASON_UNSUPPORTED_EXTENSION
                        ),
                        size_bytes=file_size,
                    )
                )
                continue

            image_files.append(file_path)
            extension = file_path.suffix.lower().lstrip(".")

            if not extension:
                extension = "unknown"

            extension_counts[extension] = extension_counts.get(
                extension,
                0,
            ) + 1

        return {
            "image_files": image_files,
            "non_artwork_files": non_artwork_files,
            "folder_size_bytes": folder_size_bytes,
            "extension_counts": dict(
                sorted(
                    extension_counts.items(),
                    key=lambda item: item[0],
                )
            ),
        }

    def _get_image_files(self, folder_path: Path) -> list[Path]:
        return self._scan_folder_files(folder_path)["image_files"]

    def _calculate_folder_size(self, folder_path: Path) -> int:
        return self._scan_folder_files(folder_path)["folder_size_bytes"]

    def _count_extensions(
        self,
        image_files: list[Path],
    ) -> dict[str, int]:
        extension_counts: dict[str, int] = {}

        for file_path in image_files:
            extension = file_path.suffix.lower().lstrip(".")

            if not extension:
                extension = "unknown"

            extension_counts[extension] = extension_counts.get(
                extension,
                0,
            ) + 1

        return dict(
            sorted(
                extension_counts.items(),
                key=lambda item: item[0],
            )
        )

    def _extract_artwork_ids(
        self,
        folder_path: Path,
        image_files: list[Path],
        non_artwork_files: list[dict],
    ) -> dict:
        artwork_ids: set[str] = set()
        invalid_file_names: list[str] = []
        collected_non_artwork_files = list(non_artwork_files)

        for file_path in image_files:
            artwork_id = self._extract_artwork_id(file_path)

            if artwork_id:
                artwork_ids.add(artwork_id)
                continue

            invalid_file_names.append(file_path.name)
            collected_non_artwork_files.append(
                self.non_artwork_collector.build_record(
                    file_path=file_path,
                    folder_path=folder_path,
                    reason=(
                        self.non_artwork_collector
                        .REASON_ARTWORK_ID_NOT_FOUND
                    ),
                    size_bytes=self._safe_get_file_size(file_path),
                )
            )

        return {
            "artwork_ids": sorted(artwork_ids, key=int, reverse=True),
            "invalid_file_names": invalid_file_names,
            "non_artwork_files": collected_non_artwork_files,
        }

    def _extract_artwork_id(
        self,
        file_path: Path,
    ) -> str:
        pixiv_match = self.PIXIV_ARTWORK_FILE_PATTERN.search(file_path.stem)

        if pixiv_match:
            return pixiv_match.group(1)

        fallback_match = self.ARTWORK_ID_PATTERN.search(file_path.stem)

        if fallback_match:
            return fallback_match.group(1)

        return ""

    def _safe_get_file_size(
        self,
        file_path: Path,
    ) -> int:
        try:
            return file_path.stat().st_size
        except OSError:
            return 0
