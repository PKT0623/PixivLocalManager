from pathlib import Path
import re


class ArtworkExtractorMixin:
    PIXIV_ARTWORK_FILE_PATTERN = re.compile(
        r"^(\d{5,})(?:_p\d+)?(?:\D.*)?$"
    )
    ARTWORK_ID_PATTERN = re.compile(r"(\d{5,})")

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
