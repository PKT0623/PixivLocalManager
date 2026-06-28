from pathlib import Path


class FileScannerMixin:
    def _scan_folder_files(
        self,
        folder_path: Path,
    ) -> dict:
        image_files: list[Path] = []
        non_artwork_files: list[dict] = []
        folder_size_bytes = 0
        extension_counts: dict[str, int] = {}
        image_extensions = self.image_extensions

        for file_path in folder_path.rglob("*"):
            if not file_path.is_file():
                continue

            file_size = self._safe_get_file_size_or_none(file_path)

            if file_size is None:
                non_artwork_files.append(
                    self.non_artwork_collector.build_record(
                        file_path=file_path,
                        folder_path=folder_path,
                        reason=(
                            self.non_artwork_collector.REASON_SCAN_ERROR
                        ),
                    )
                )
                continue

            folder_size_bytes += file_size

            if file_size <= 0:
                non_artwork_files.append(
                    self.non_artwork_collector.build_record(
                        file_path=file_path,
                        folder_path=folder_path,
                        reason=(
                            self.non_artwork_collector.REASON_EMPTY_FILE
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
            self._increase_extension_count(
                extension_counts=extension_counts,
                file_path=file_path,
            )

        return {
            "image_files": image_files,
            "non_artwork_files": non_artwork_files,
            "folder_size_bytes": folder_size_bytes,
            "extension_counts": self._sort_extension_counts(
                extension_counts
            ),
        }

    def _get_image_files(
        self,
        folder_path: Path,
    ) -> list[Path]:
        return self._scan_folder_files(folder_path)["image_files"]

    def _calculate_folder_size(
        self,
        folder_path: Path,
    ) -> int:
        return self._scan_folder_files(folder_path)["folder_size_bytes"]

    def _count_extensions(
        self,
        image_files: list[Path],
    ) -> dict[str, int]:
        extension_counts: dict[str, int] = {}

        for file_path in image_files:
            self._increase_extension_count(
                extension_counts=extension_counts,
                file_path=file_path,
            )

        return self._sort_extension_counts(extension_counts)

    def _increase_extension_count(
        self,
        extension_counts: dict[str, int],
        file_path: Path,
    ) -> None:
        extension = file_path.suffix.lower().lstrip(".")

        if not extension:
            extension = "unknown"

        extension_counts[extension] = extension_counts.get(
            extension,
            0,
        ) + 1

    def _sort_extension_counts(
        self,
        extension_counts: dict[str, int],
    ) -> dict[str, int]:
        return dict(
            sorted(
                extension_counts.items(),
                key=lambda item: item[0],
            )
        )

    def _safe_get_file_size_or_none(
        self,
        file_path: Path,
    ) -> int | None:
        try:
            return file_path.stat().st_size
        except OSError:
            return None
