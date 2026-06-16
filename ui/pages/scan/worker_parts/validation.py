from pathlib import Path


class ValidationMixin:
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

    def _validate_artist_folder(
        self,
        folder_path: Path,
        index: int,
        total: int,
        seen_folder_paths: set[str],
        seen_pixiv_ids: set[str],
        existing_by_pixiv_id: dict[str, dict],
        existing_by_folder_path: dict[str, dict],
        registered_pixiv_ids: set[str],
    ) -> dict:
        log_rows = []
        folder_key = str(folder_path.resolve()).casefold()
        artist_name = folder_path.name
        pixiv_id = "-"
        can_scan = True

        if folder_key in seen_folder_paths:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="중복 폴더 경로입니다. 이후 항목은 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        seen_folder_paths.add(folder_key)

        if not folder_path.exists():
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="폴더를 찾을 수 없습니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        if not folder_path.is_dir():
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="폴더 경로가 아닙니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        if not self.folder_scanner.has_image_files(folder_path):
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="이미지 파일이 없습니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        artist_name, pixiv_id = (
            self.folder_scan_service.parse_artist_folder_name(
                folder_path.name
            )
        )
        rule_status = self.folder_scan_service.get_folder_name_rule_status(
            folder_path.name
        )

        if not pixiv_id:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name or folder_path.name,
                    pixiv_id="-",
                    folder_path=folder_path,
                    message="Pixiv ID가 없습니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        if not artist_name:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=folder_path.name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="작가명을 찾을 수 없습니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        if pixiv_id in seen_pixiv_ids:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message=(
                        "이번 스캔 대상 안에서 중복 Pixiv ID가 발견됐습니다. "
                        "이후 항목은 제외합니다."
                    ),
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        seen_pixiv_ids.add(pixiv_id)

        if rule_status["level"] == "warning" and not self.preview_mode:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="경고",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message=rule_status["message"],
                )
            )

        existing_by_folder = existing_by_folder_path.get(folder_key)

        if existing_by_folder is not None:
            existing_pixiv_id = str(existing_by_folder.get("pixiv_id", ""))

            if existing_pixiv_id != pixiv_id:
                log_rows.append(
                    self._build_validation_row(
                        index=index,
                        total=total,
                        result="오류",
                        artist_name=artist_name,
                        pixiv_id=pixiv_id,
                        folder_path=folder_path,
                        message=(
                            "같은 폴더 경로가 다른 Pixiv ID로 이미 "
                            "등록되어 있습니다. 스캔에서 제외합니다."
                        ),
                    )
                )
                can_scan = False

        if pixiv_id in existing_by_pixiv_id:
            registered_pixiv_ids.add(pixiv_id)

        return {
            "can_scan": can_scan,
            "log_rows": log_rows,
        }

    def _build_existing_pixiv_id_map(
        self,
        artists: list[dict],
    ) -> dict[str, dict]:
        result = {}

        for artist in artists:
            pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

            if not pixiv_id:
                continue

            result[pixiv_id] = artist

        return result

    def _build_existing_folder_path_map(
        self,
        artists: list[dict],
    ) -> dict[str, dict]:
        result = {}

        for artist in artists:
            folder_path = str(artist.get("folder_path", "") or "").strip()

            if not folder_path:
                continue

            result[str(Path(folder_path).resolve()).casefold()] = artist

        return result
