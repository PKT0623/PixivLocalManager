from pathlib import Path


class ValidationMainMixin:
    def _validate_artist_folders(
        self,
        artist_folders: list[Path],
    ) -> dict:
        log_rows = []
        scannable_folders = []
        registered_pixiv_ids = set()

        seen_folder_paths = set()
        seen_pixiv_ids = set()
        existing_artists = self.artist_service.get_all_artists()
        existing_by_pixiv_id = self._build_existing_pixiv_id_map(
            existing_artists
        )
        existing_by_folder_path = self._build_existing_folder_path_map(
            existing_artists
        )

        total = len(artist_folders)

        for index, folder_path in enumerate(artist_folders, start=1):
            result = self._validate_artist_folder(
                folder_path=folder_path,
                index=index,
                total=total,
                seen_folder_paths=seen_folder_paths,
                seen_pixiv_ids=seen_pixiv_ids,
                existing_by_pixiv_id=existing_by_pixiv_id,
                existing_by_folder_path=existing_by_folder_path,
                registered_pixiv_ids=registered_pixiv_ids,
            )

            log_rows.extend(result["log_rows"])

            if result["can_scan"]:
                scannable_folders.append(folder_path)

        if registered_pixiv_ids and not self.preview_mode:
            log_rows.append(
                self._build_validation_row(
                    index=0,
                    total=total,
                    result="경고",
                    artist_name="이미 등록된 Pixiv ID",
                    pixiv_id="-",
                    folder_path=Path(self.root_folder_path),
                    message=(
                        f"이미 등록된 Pixiv ID "
                        f"{len(registered_pixiv_ids)}개를 발견했습니다. "
                        "해당 항목은 기존 작가 정보 갱신 대상으로 "
                        "처리합니다."
                    ),
                )
            )

        return {
            "log_rows": log_rows,
            "scannable_folders": scannable_folders,
        }
