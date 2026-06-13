from dataclasses import dataclass
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
    ARTWORK_ID_PATTERN = re.compile(r"(\d{5,})")

    def scan_folder(self, folder_path: str) -> FolderScanResult:
        path = Path(folder_path)

        if not path.exists():
            raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")

        if not path.is_dir():
            raise NotADirectoryError(f"폴더 경로가 아닙니다: {folder_path}")

        artist_name, pixiv_id = self._parse_artist_folder_name(path.name)

        image_files = self._get_image_files(path)
        folder_size_bytes = self._calculate_folder_size(path)
        local_artwork_ids = self._extract_artwork_ids(image_files)

        return FolderScanResult(
            artist_name=artist_name,
            pixiv_id=pixiv_id,
            folder_path=str(path),
            folder_size_bytes=folder_size_bytes,
            folder_file_count=len(image_files),
            folder_artwork_count=len(local_artwork_ids),
            local_latest_artwork_ids=",".join(local_artwork_ids),
        )

    def _parse_artist_folder_name(self, folder_name: str) -> tuple[str, str]:
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

    def _extract_artwork_ids(self, image_files: list[Path]) -> list[str]:
        artwork_ids: set[str] = set()

        for file_path in image_files:
            match = self.ARTWORK_ID_PATTERN.search(file_path.stem)

            if match:
                artwork_ids.add(match.group(1))

        return sorted(artwork_ids, key=int, reverse=True)
