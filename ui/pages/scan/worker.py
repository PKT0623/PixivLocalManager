from datetime import datetime
from pathlib import Path
import time

from PySide6.QtCore import QObject, Signal

from app.services.artist import ArtistService
from app.services.artwork_status_service import ArtworkStatusService
from app.services.scan import FolderScanService

from .folder_scanner import FolderScanner
from .worker_parts import (
    PreviewBuilderMixin,
    ResultBuilderMixin,
    RuntimeUtilsMixin,
    StatisticsMixin,
    ValidationMixin,
)


class ScanWorker(
    QObject,
    ValidationMixin,
    PreviewBuilderMixin,
    ResultBuilderMixin,
    StatisticsMixin,
    RuntimeUtilsMixin,
):
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

    def _scan_artist_folder(self, folder_path: Path) -> dict:
        return self.artist_service.save_scanned_artist(
            str(folder_path)
        )
