from dataclasses import dataclass, field
from pathlib import Path
import re


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


class FolderScanService:
    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".bmp",
    }

    BRACKETED_PIXIV_ID_PATTERN = re.compile(r"[\[\(](\d{5,})[\]\)]")
    TRAILING_PIXIV_ID_PATTERN = re.compile(r"[-_ ]+(\d{5,})$")
    ANY_PIXIV_ID_PATTERN = re.compile(r"(\d{5,})")

    PIXIV_ARTWORK_FILE_PATTERN = re.compile(
        r"^(\d{5,})(?:_p\d+)?(?:\D.*)?$"
    )
    ARTWORK_ID_PATTERN = re.compile(r"(\d{5,})")

    def scan_folder(self, folder_path: str) -> FolderScanResult:
        path = Path(folder_path)

        if not path.exists():
            raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")

        if not path.is_dir():
            raise NotADirectoryError(f"폴더 경로가 아닙니다: {folder_path}")

        artist_name, pixiv_id = self.parse_artist_folder_name(path.name)

        image_files = self._get_image_files(path)
        folder_size_bytes = self._calculate_folder_size(path)
        artwork_result = self._extract_artwork_ids(image_files)
        extension_counts = self._count_extensions(image_files)

        return FolderScanResult(
            artist_name=artist_name,
            pixiv_id=pixiv_id,
            folder_path=str(path),
            folder_size_bytes=folder_size_bytes,
            folder_file_count=len(image_files),
            folder_artwork_count=len(artwork_result["artwork_ids"]),
            local_latest_artwork_ids=",".join(artwork_result["artwork_ids"]),
            extension_counts=extension_counts,
            invalid_artwork_file_names=artwork_result["invalid_file_names"],
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

    def _get_image_files(self, folder_path: Path) -> list[Path]:
        image_files: list[Path] = []

        for file_path in folder_path.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.IMAGE_EXTENSIONS
            ):
                image_files.append(file_path)

        return image_files

    def _calculate_folder_size(self, folder_path: Path) -> int:
        total_size = 0

        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

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

    def _extract_artwork_ids(self, image_files: list[Path]) -> dict:
        artwork_ids: set[str] = set()
        invalid_file_names: list[str] = []

        for file_path in image_files:
            artwork_id = self._extract_artwork_id(file_path)

            if artwork_id:
                artwork_ids.add(artwork_id)
                continue

            invalid_file_names.append(file_path.name)

        return {
            "artwork_ids": sorted(artwork_ids, key=int, reverse=True),
            "invalid_file_names": invalid_file_names,
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
