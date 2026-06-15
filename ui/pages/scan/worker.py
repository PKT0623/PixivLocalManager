from datetime import datetime
from pathlib import Path
import time

from PySide6.QtCore import QObject, Signal

from app.services.artist_service import ArtistService
from app.services.artwork_status_service import ArtworkStatusService
from app.services.folder_scan_service import FolderScanService

from .folder_scanner import FolderScanner


class ScanWorker(QObject):
    log_message_requested = Signal(str)
    scan_result_requested = Signal(dict)
    preview_result_requested = Signal(list)
    preview_summary_updated = Signal(dict)
    progress_updated = Signal(int, int)
    current_folder_changed = Signal(str)
    target_count_changed = Signal(int)
    summary_updated = Signal(dict)
    statistics_updated = Signal(dict)
    runtime_info_updated = Signal(dict)
    paused = Signal(dict)
    stopped = Signal(dict)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(
        self,
        root_folder_path: str,
        target_folder_paths: list[str] | None = None,
        preview_mode: bool = False,
        resume_payload: dict | None = None,
    ):
        super().__init__()

        self.root_folder_path = root_folder_path
        self.target_folder_paths = target_folder_paths
        self.preview_mode = preview_mode
        self.resume_payload = resume_payload or {}

        self.artist_service = ArtistService()
        self.folder_scanner = FolderScanner()
        self.folder_scan_service = FolderScanService()
        self.status_service = ArtworkStatusService()

        self.stop_requested = False
        self.pause_requested = False

    def request_stop(self):
        self.stop_requested = True
        self.pause_requested = False

    def request_pause(self):
        self.pause_requested = True

    def run(self):
        if self.preview_mode:
            self._run_preview()
            return

        self._run_scan()

    def _run_preview(self):
        started_at = datetime.now()
        start_timestamp = time.monotonic()

        try:
            self.runtime_info_updated.emit(
                self._build_runtime_info(
                    started_at=started_at,
                    start_timestamp=start_timestamp,
                    current=0,
                    total=0,
                )
            )

            artist_folders = self._get_artist_folders()
            validation_result = self._validate_artist_folders(artist_folders)

            preview_rows = []

            for row_data in validation_result["log_rows"]:
                if row_data.get("result") == "오류":
                    preview_rows.append(
                        self._build_preview_error_row(row_data)
                    )

            artist_folders = validation_result["scannable_folders"]
            run_state = self._create_run_state(
                started_at=started_at,
                start_timestamp=start_timestamp,
                artist_folders=artist_folders,
            )

            self._restore_run_state_if_needed(run_state)

            self.target_count_changed.emit(run_state["total_count"])
            self.progress_updated.emit(
                run_state["completed_count"],
                run_state["total_count"],
            )

            if not artist_folders and not preview_rows:
                self.log_message_requested.emit(
                    "미리보기 가능한 작가 폴더가 없습니다."
                )
                self.preview_result_requested.emit([])
                self.preview_summary_updated.emit(self._create_summary())
                self.finished.emit(
                    self._build_finished_result(
                        started_at=started_at,
                        start_timestamp=start_timestamp,
                        total=0,
                        summary=self._create_summary(),
                        statistics=self._create_statistics(),
                    )
                )
                return

            if not self.resume_payload:
                self.log_message_requested.emit(
                    f"스캔 미리보기 시작: {len(artist_folders)}개"
                )

            existing_artists = self.artist_service.get_all_artists()
            existing_by_pixiv_id = self._build_existing_pixiv_id_map(
                existing_artists
            )

            for local_index, folder_path in enumerate(
                artist_folders,
                start=1,
            ):
                self.current_folder_changed.emit(folder_path.name)

                try:
                    row = self._preview_artist_folder(
                        folder_path=folder_path,
                        existing_by_pixiv_id=existing_by_pixiv_id,
                    )
                    preview_rows.append(row)
                    self._increase_preview_summary(run_state["summary"], row)
                    self._increase_statistics(
                        run_state["statistics"],
                        row.get("scan_result"),
                    )
                except Exception as error:
                    error_row = self._build_preview_exception_row(
                        folder_path,
                        error,
                    )
                    preview_rows.append(error_row)
                    self._increase_preview_summary(
                        run_state["summary"],
                        error_row,
                    )

                self._increase_completed_count(run_state)
                self.preview_summary_updated.emit(run_state["summary"])
                self.statistics_updated.emit(run_state["statistics"])
                self.progress_updated.emit(
                    run_state["completed_count"],
                    run_state["total_count"],
                )
                self.runtime_info_updated.emit(
                    self._build_runtime_info(
                        started_at=started_at,
                        start_timestamp=start_timestamp,
                        current=run_state["completed_count"],
                        total=run_state["total_count"],
                    )
                )

                if self._should_stop_after_preview_item(
                    run_state,
                    artist_folders,
                    local_index,
                    preview_rows,
                ):
                    return

                if self._should_pause_after_preview_item(
                    run_state,
                    artist_folders,
                    local_index,
                    preview_rows,
                ):
                    return

            self.current_folder_changed.emit("-")
            self.preview_result_requested.emit(
                self._strip_preview_runtime_objects(preview_rows)
            )
            self.preview_summary_updated.emit(run_state["summary"])
            self.log_message_requested.emit(
                "스캔 미리보기 완료: "
                f"신규 {run_state['summary']['created']}개, "
                f"업데이트 {run_state['summary']['updated']}개, "
                f"변경 없음 {run_state['summary']['unchanged']}개, "
                f"오류 예상 {run_state['summary']['failed']}개"
            )
        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit(
            self._build_finished_result(
                started_at=started_at,
                start_timestamp=start_timestamp,
                total=run_state["total_count"],
                summary=run_state["summary"],
                statistics=run_state["statistics"],
            )
        )

    def _run_scan(self):
        started_at = datetime.now()
        start_timestamp = time.monotonic()

        try:
            self.runtime_info_updated.emit(
                self._build_runtime_info(
                    started_at=started_at,
                    start_timestamp=start_timestamp,
                    current=0,
                    total=0,
                )
            )

            artist_folders = self._get_artist_folders()
            validation_result = self._validate_artist_folders(artist_folders)

            for row_data in validation_result["log_rows"]:
                self.scan_result_requested.emit(row_data)

            artist_folders = validation_result["scannable_folders"]
            run_state = self._create_run_state(
                started_at=started_at,
                start_timestamp=start_timestamp,
                artist_folders=artist_folders,
            )

            self._restore_run_state_if_needed(run_state)

            self.target_count_changed.emit(run_state["total_count"])
            self.progress_updated.emit(
                run_state["completed_count"],
                run_state["total_count"],
            )

            if not artist_folders:
                self.log_message_requested.emit(
                    "스캔 가능한 작가 폴더가 없습니다."
                )
                finished_result = self._build_finished_result(
                    started_at=started_at,
                    start_timestamp=start_timestamp,
                    total=0,
                    summary=self._create_summary(),
                    statistics=self._create_statistics(),
                )
                self.finished.emit(finished_result)
                return

            self.log_message_requested.emit(
                f"스캔 대상 작가 폴더: {len(artist_folders)}개"
            )

            self.summary_updated.emit(run_state["summary"])
            self.statistics_updated.emit(run_state["statistics"])

            for local_index, folder_path in enumerate(
                artist_folders,
                start=1,
            ):
                self.current_folder_changed.emit(folder_path.name)

                try:
                    result = self._scan_artist_folder(folder_path)
                    action = result.get("action")
                    artist = result.get("artist") or {}
                    scan_result = result.get("scan_result")

                    result_label = self._result_label(action)
                    self._increase_summary(run_state["summary"], action)
                    self._increase_statistics(
                        run_state["statistics"],
                        scan_result,
                    )

                    self.scan_result_requested.emit(
                        self._build_scan_result_row(
                            index=run_state["completed_count"] + 1,
                            total=run_state["total_count"],
                            result=result_label,
                            artist=artist,
                            folder_path=folder_path,
                        )
                    )
                except Exception as error:
                    run_state["summary"]["failed"] += 1

                    self.scan_result_requested.emit(
                        self._build_failed_result_row(
                            index=run_state["completed_count"] + 1,
                            total=run_state["total_count"],
                            folder_path=folder_path,
                            error=error,
                        )
                    )

                self._increase_completed_count(run_state)
                self.summary_updated.emit(run_state["summary"])
                self.statistics_updated.emit(run_state["statistics"])
                self.progress_updated.emit(
                    run_state["completed_count"],
                    run_state["total_count"],
                )
                self.runtime_info_updated.emit(
                    self._build_runtime_info(
                        started_at=started_at,
                        start_timestamp=start_timestamp,
                        current=run_state["completed_count"],
                        total=run_state["total_count"],
                    )
                )

                if self._should_stop_after_item(
                    run_state,
                    artist_folders,
                    local_index,
                ):
                    return

                if self._should_pause_after_item(
                    run_state,
                    artist_folders,
                    local_index,
                ):
                    return

            self.current_folder_changed.emit("-")
            self.log_message_requested.emit(
                "전체 스캔 완료: "
                f"등록 {run_state['summary']['created']}개, "
                f"업데이트 {run_state['summary']['updated']}개, "
                f"변경 없음 {run_state['summary']['unchanged']}개, "
                f"실패 {run_state['summary']['failed']}개, "
                f"총 파일 {run_state['statistics']['total_file_count']}개, "
                f"총 작품 {run_state['statistics']['total_artwork_count']}개"
            )
        except Exception as error:
            self.failed.emit(str(error))
            return

        finished_result = self._build_finished_result(
            started_at=started_at,
            start_timestamp=start_timestamp,
            total=run_state["total_count"],
            summary=run_state["summary"],
            statistics=run_state["statistics"],
        )
        self.finished.emit(finished_result)

    def _create_run_state(
        self,
        started_at: datetime,
        start_timestamp: float,
        artist_folders: list[Path],
    ) -> dict:
        return {
            "started_at": started_at,
            "start_timestamp": start_timestamp,
            "root_folder_path": self.root_folder_path,
            "preview_mode": self.preview_mode,
            "total_count": len(artist_folders),
            "completed_count": 0,
            "summary": self._create_summary(),
            "statistics": self._create_statistics(),
        }

    def _restore_run_state_if_needed(
        self,
        run_state: dict,
    ):
        if not self.resume_payload:
            return

        run_state["total_count"] = int(
            self.resume_payload.get("total_count", 0)
            or run_state["total_count"]
        )
        run_state["completed_count"] = int(
            self.resume_payload.get("completed_count", 0) or 0
        )
        run_state["summary"] = dict(
            self.resume_payload.get("summary", {}) or self._create_summary()
        )
        run_state["statistics"] = dict(
            self.resume_payload.get("statistics", {})
            or self._create_statistics()
        )

    def _increase_completed_count(
        self,
        run_state: dict,
    ):
        run_state["completed_count"] = int(
            run_state.get("completed_count", 0) or 0
        ) + 1

    def _should_stop_after_item(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
    ) -> bool:
        if not self.stop_requested:
            return False

        self.current_folder_changed.emit("-")
        self.stopped.emit(
            self._build_control_payload(
                run_state,
                artist_folders,
                local_index,
            )
        )
        return True

    def _should_pause_after_item(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
    ) -> bool:
        if not self.pause_requested:
            return False

        self.current_folder_changed.emit("-")
        self.paused.emit(
            self._build_control_payload(
                run_state,
                artist_folders,
                local_index,
            )
        )
        return True

    def _should_stop_after_preview_item(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
        preview_rows: list[dict],
    ) -> bool:
        if not self.stop_requested:
            return False

        self.current_folder_changed.emit("-")
        self.preview_result_requested.emit(
            self._strip_preview_runtime_objects(preview_rows)
        )
        self.stopped.emit(
            self._build_control_payload(
                run_state,
                artist_folders,
                local_index,
            )
        )
        return True

    def _should_pause_after_preview_item(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
        preview_rows: list[dict],
    ) -> bool:
        if not self.pause_requested:
            return False

        self.current_folder_changed.emit("-")
        self.preview_result_requested.emit(
            self._strip_preview_runtime_objects(preview_rows)
        )
        self.paused.emit(
            self._build_control_payload(
                run_state,
                artist_folders,
                local_index,
            )
        )
        return True

    def _build_control_payload(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
    ) -> dict:
        remaining_folders = artist_folders[local_index:]

        return {
            "root_folder_path": self.root_folder_path,
            "preview_mode": self.preview_mode,
            "total_count": int(run_state.get("total_count", 0) or 0),
            "completed_count": int(run_state.get("completed_count", 0) or 0),
            "summary": dict(run_state.get("summary", {}) or {}),
            "statistics": dict(run_state.get("statistics", {}) or {}),
            "remaining_folder_paths": [
                str(folder_path)
                for folder_path in remaining_folders
            ],
        }

    def _get_artist_folders(self) -> list[Path]:
        if self.target_folder_paths is not None:
            return [
                Path(folder_path)
                for folder_path in self.target_folder_paths
                if str(folder_path or "").strip()
            ]

        root_folder = Path(self.root_folder_path)

        if not root_folder.exists() or not root_folder.is_dir():
            raise ValueError("선택한 폴더가 존재하지 않습니다.")

        return self.folder_scanner.find_artist_folders(
            root_folder,
            max_depth=3,
        )

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

    def _preview_artist_folder(
        self,
        folder_path: Path,
        existing_by_pixiv_id: dict[str, dict],
    ) -> dict:
        scan_result = self.folder_scan_service.scan_folder(str(folder_path))
        pixiv_id = str(scan_result.pixiv_id or "").strip()
        existing_artist = existing_by_pixiv_id.get(pixiv_id)

        if existing_artist is None:
            return self._build_preview_row(
                preview_result="신규 등록 예정",
                can_scan=True,
                scan_result=scan_result,
                existing_artist=None,
                message="새 작가로 등록됩니다.",
            )

        update_status = self.status_service.calculate_status(
            scan_result.local_latest_artwork_ids,
            existing_artist.get("pixiv_latest_artwork_ids", ""),
        )

        update_data = dict(existing_artist)
        update_data["artist_name"] = scan_result.artist_name
        update_data["pixiv_id"] = scan_result.pixiv_id
        update_data["folder_path"] = scan_result.folder_path
        update_data["folder_size_bytes"] = scan_result.folder_size_bytes
        update_data["folder_file_count"] = scan_result.folder_file_count
        update_data["folder_artwork_count"] = scan_result.folder_artwork_count
        update_data["local_latest_artwork_ids"] = (
            scan_result.local_latest_artwork_ids
        )
        update_data["update_status"] = update_status.status

        change_message = self._build_preview_change_message(
            existing_artist,
            update_data,
        )

        if change_message:
            return self._build_preview_row(
                preview_result="업데이트 예정",
                can_scan=True,
                scan_result=scan_result,
                existing_artist=existing_artist,
                message=change_message,
            )

        return self._build_preview_row(
            preview_result="변경 없음 예정",
            can_scan=True,
            scan_result=scan_result,
            existing_artist=existing_artist,
            message="등록된 정보와 변경 사항이 없습니다.",
        )

    def _build_preview_row(
        self,
        preview_result: str,
        can_scan: bool,
        scan_result,
        existing_artist: dict | None,
        message: str,
    ) -> dict:
        return {
            "preview_result": preview_result,
            "can_scan": can_scan,
            "artist_id": (
                existing_artist.get("id")
                if existing_artist is not None
                else None
            ),
            "artist_name": scan_result.artist_name or "-",
            "pixiv_id": scan_result.pixiv_id or "-",
            "artwork_count": scan_result.folder_artwork_count,
            "file_count": scan_result.folder_file_count,
            "folder_path": scan_result.folder_path,
            "message": message,
            "scan_result": scan_result,
        }

    def _build_preview_error_row(
        self,
        row_data: dict,
    ) -> dict:
        return {
            "preview_result": "오류 예상",
            "can_scan": False,
            "artist_id": None,
            "artist_name": row_data.get("artist_name", "-"),
            "pixiv_id": row_data.get("pixiv_id", "-"),
            "artwork_count": "-",
            "file_count": "-",
            "folder_path": row_data.get("folder_path", "-"),
            "message": row_data.get("error_message", "-"),
        }

    def _build_preview_exception_row(
        self,
        folder_path: Path,
        error: Exception,
    ) -> dict:
        return {
            "preview_result": "오류 예상",
            "can_scan": False,
            "artist_id": None,
            "artist_name": folder_path.name,
            "pixiv_id": "-",
            "artwork_count": "-",
            "file_count": "-",
            "folder_path": str(folder_path),
            "message": str(error),
        }

    def _strip_preview_runtime_objects(
        self,
        rows: list[dict],
    ) -> list[dict]:
        result = []

        for row in rows:
            item = dict(row)
            item.pop("scan_result", None)
            result.append(item)

        return result

    def _build_preview_change_message(
        self,
        existing_artist: dict,
        update_data: dict,
    ) -> str:
        messages = []

        change_targets = [
            ("작가명", "artist_name", self._format_text_change_value),
            ("폴더 경로", "folder_path", self._format_text_change_value),
            ("작품 수", "folder_artwork_count", self._format_number_change_value),
            ("파일 수", "folder_file_count", self._format_number_change_value),
            ("폴더 크기", "folder_size_bytes", self._format_size_change_value),
            ("업데이트 상태", "update_status", self._format_text_change_value),
        ]

        for label, field_name, formatter in change_targets:
            old_value = existing_artist.get(field_name)
            new_value = update_data.get(field_name)

            if not self._is_value_changed(old_value, new_value):
                continue

            messages.append(
                f"{label} {formatter(old_value)} → {formatter(new_value)}"
            )

        old_artwork_ids = str(
            existing_artist.get("local_latest_artwork_ids", "") or ""
        )
        new_artwork_ids = str(
            update_data.get("local_latest_artwork_ids", "") or ""
        )

        if self._is_value_changed(old_artwork_ids, new_artwork_ids):
            messages.extend(
                self._build_artwork_id_change_messages(
                    old_artwork_ids,
                    new_artwork_ids,
                )
            )

        return " / ".join(messages)

    def _build_artwork_id_change_messages(
        self,
        old_value: str,
        new_value: str,
    ) -> list[str]:
        old_ids = self._split_artwork_ids(old_value)
        new_ids = self._split_artwork_ids(new_value)

        added_ids = [
            artwork_id
            for artwork_id in new_ids
            if artwork_id not in old_ids
        ]
        removed_ids = [
            artwork_id
            for artwork_id in old_ids
            if artwork_id not in new_ids
        ]

        messages = []

        if added_ids:
            messages.append(
                "신규 작품 ID "
                + ", ".join(added_ids[:5])
                + self._format_overflow_count(len(added_ids), 5)
            )

        if removed_ids:
            messages.append(
                "제외된 작품 ID "
                + ", ".join(removed_ids[:5])
                + self._format_overflow_count(len(removed_ids), 5)
            )

        if not messages:
            messages.append("최신 작품 ID 순서 변경")

        return messages

    def _split_artwork_ids(
        self,
        value: str,
    ) -> list[str]:
        return [
            item.strip()
            for item in str(value or "").split(",")
            if item.strip()
        ]

    def _format_overflow_count(
        self,
        total_count: int,
        display_limit: int,
    ) -> str:
        remain_count = int(total_count or 0) - int(display_limit or 0)

        if remain_count <= 0:
            return ""

        return f" 외 {remain_count}개"

    def _is_value_changed(
        self,
        old_value,
        new_value,
    ) -> bool:
        return str(old_value or "") != str(new_value or "")

    def _format_text_change_value(
        self,
        value,
    ) -> str:
        value = str(value or "").strip()

        if not value:
            return "-"

        return value

    def _format_number_change_value(
        self,
        value,
    ) -> str:
        try:
            return str(int(value or 0))
        except (TypeError, ValueError):
            return "0"

    def _format_size_change_value(
        self,
        value,
    ) -> str:
        try:
            size = int(value or 0)
        except (TypeError, ValueError):
            size = 0

        if size >= 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"

        if size >= 1024:
            return f"{size / 1024:.2f} KB"

        return f"{size} B"

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

    def _scan_artist_folder(self, folder_path: Path) -> dict:
        return self.artist_service.save_scanned_artist(
            str(folder_path)
        )

    def _result_label(self, action: str | None) -> str:
        if action == "created":
            return "등록"

        if action == "updated":
            return "업데이트"

        if action == "unchanged":
            return "변경 없음"

        return "업데이트"

    def _create_summary(self) -> dict:
        return {
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "failed": 0,
        }

    def _create_statistics(self) -> dict:
        return {
            "total_file_count": 0,
            "total_artwork_count": 0,
            "extension_counts": {},
        }

    def _increase_preview_summary(
        self,
        summary: dict,
        row: dict,
    ):
        preview_result = str(row.get("preview_result", "") or "")

        if preview_result == "신규 등록 예정":
            summary["created"] += 1
            return

        if preview_result == "업데이트 예정":
            summary["updated"] += 1
            return

        if preview_result == "변경 없음 예정":
            summary["unchanged"] += 1
            return

        if preview_result == "오류 예상":
            summary["failed"] += 1

    def _increase_summary(
        self,
        summary: dict,
        action: str | None,
    ):
        if action == "created":
            summary["created"] += 1
            return

        if action == "updated":
            summary["updated"] += 1
            return

        if action == "unchanged":
            summary["unchanged"] += 1
            return

        summary["updated"] += 1

    def _increase_statistics(
        self,
        statistics: dict,
        scan_result,
    ):
        if scan_result is None:
            return

        statistics["total_file_count"] += int(
            getattr(scan_result, "folder_file_count", 0) or 0
        )
        statistics["total_artwork_count"] += int(
            getattr(scan_result, "folder_artwork_count", 0) or 0
        )

        extension_counts = getattr(scan_result, "extension_counts", {}) or {}

        for extension, count in extension_counts.items():
            statistics["extension_counts"][extension] = (
                statistics["extension_counts"].get(extension, 0)
                + int(count or 0)
            )

    def _build_runtime_info(
        self,
        started_at: datetime,
        start_timestamp: float,
        current: int,
        total: int,
    ) -> dict:
        elapsed_seconds = max(
            0,
            int(time.monotonic() - start_timestamp),
        )
        speed = 0.0

        if elapsed_seconds > 0 and current > 0:
            speed = current / elapsed_seconds

        remaining_seconds = None

        if speed > 0 and total > current:
            remaining_seconds = int((total - current) / speed)

        return {
            "start_time_text": started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_time_text": self._format_seconds(elapsed_seconds),
            "speed_text": self._format_speed(speed),
            "estimated_time_text": self._format_remaining_time(
                remaining_seconds
            ),
        }

    def _build_finished_result(
        self,
        started_at: datetime,
        start_timestamp: float,
        total: int,
        summary: dict,
        statistics: dict,
    ) -> dict:
        finished_at = datetime.now()
        duration_seconds = max(
            0,
            int(time.monotonic() - start_timestamp),
        )

        return {
            "started_at": started_at.isoformat(),
            "started_at_text": started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "finished_at": finished_at.isoformat(),
            "finished_at_text": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": duration_seconds,
            "duration_text": self._format_seconds(duration_seconds),
            "root_folder_path": self.root_folder_path,
            "total": total,
            "created": int(summary.get("created", 0) or 0),
            "updated": int(summary.get("updated", 0) or 0),
            "unchanged": int(summary.get("unchanged", 0) or 0),
            "failed": int(summary.get("failed", 0) or 0),
            "total_file_count": int(
                statistics.get("total_file_count", 0) or 0
            ),
            "total_artwork_count": int(
                statistics.get("total_artwork_count", 0) or 0
            ),
            "extension_counts": statistics.get("extension_counts", {}) or {},
        }

    def _format_seconds(
        self,
        seconds: int,
    ) -> str:
        seconds = max(0, int(seconds or 0))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remain_seconds = seconds % 60

        if hours > 0:
            return f"{hours}시간 {minutes}분 {remain_seconds}초"

        if minutes > 0:
            return f"{minutes}분 {remain_seconds}초"

        return f"{remain_seconds}초"

    def _format_speed(
        self,
        speed: float,
    ) -> str:
        if speed <= 0:
            return "-"

        return f"{speed:.2f}개/초"

    def _format_remaining_time(
        self,
        seconds: int | None,
    ) -> str:
        if seconds is None:
            return "-"

        return self._format_seconds(seconds)

    def _build_scan_result_row(
        self,
        index: int,
        total: int,
        result: str,
        artist: dict,
        folder_path: Path,
    ) -> dict:
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": f"{index}/{total}",
            "result": result,
            "artist_id": artist.get("id"),
            "artist_name": str(artist.get("artist_name", "") or "-"),
            "pixiv_id": str(artist.get("pixiv_id", "") or "-"),
            "artwork_count": str(artist.get("folder_artwork_count", 0)),
            "file_count": str(artist.get("folder_file_count", 0)),
            "update_status": str(artist.get("update_status", "") or "-"),
            "folder_path": str(folder_path),
            "error_message": "-",
        }

    def _build_failed_result_row(
        self,
        index: int,
        total: int,
        folder_path: Path,
        error: Exception,
    ) -> dict:
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": f"{index}/{total}",
            "result": "실패",
            "artist_id": None,
            "artist_name": folder_path.name,
            "pixiv_id": "-",
            "artwork_count": "-",
            "file_count": "-",
            "update_status": "error",
            "folder_path": str(folder_path),
            "error_message": str(error),
        }

    def _build_validation_row(
        self,
        index: int,
        total: int,
        result: str,
        artist_name: str,
        pixiv_id: str,
        folder_path: Path,
        message: str,
    ) -> dict:
        progress = "-"

        if index > 0 and total > 0:
            progress = f"{index}/{total}"

        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": progress,
            "result": result,
            "artist_id": None,
            "artist_name": artist_name or folder_path.name,
            "pixiv_id": pixiv_id or "-",
            "artwork_count": "-",
            "file_count": "-",
            "update_status": "-",
            "folder_path": str(folder_path),
            "error_message": message,
        }
