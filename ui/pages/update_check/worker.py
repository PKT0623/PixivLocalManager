import time
from datetime import datetime
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from app.database import ArtistUpdateHistoryRepository
from app.services.artist import ArtistService
from app.services.pixiv_update_service import PixivRequestError

from .worker_config import (
    DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
    DEFAULT_UPDATE_CHECK_BATCH_SIZE,
    DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
)


class UpdateCheckWorker(QObject):
    log_requested = Signal(dict)
    progress_updated = Signal(int, int)
    summary_updated = Signal(dict)
    failed_artist_detected = Signal(int)
    paused = Signal(int, int)
    finished = Signal()
    failed = Signal(str)

    def __init__(
        self,
        artist_ids: list[int],
        cancel_event: Event,
        pause_event: Event,
        skip_recent: bool = False,
        progress_offset: int = 0,
        total_count: int | None = None,
        summary: dict | None = None,
        request_interval_ms: int = DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
        batch_size: int = DEFAULT_UPDATE_CHECK_BATCH_SIZE,
        batch_rest_ms: int = DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
    ):
        super().__init__()

        self.artist_ids = artist_ids
        self.cancel_event = cancel_event
        self.pause_event = pause_event
        self.skip_recent = skip_recent
        self.progress_offset = progress_offset
        self.total_count = total_count or len(artist_ids)
        self.request_interval_ms = max(0, int(request_interval_ms))
        self.batch_size = max(1, int(batch_size))
        self.batch_rest_ms = max(0, int(batch_rest_ms))
        self.artist_service = None
        self.history_repo = ArtistUpdateHistoryRepository()
        self.has_finished = False
        self.has_paused = False
        self.summary = summary or {
            "total": 0,
            "latest": 0,
            "need_update": 0,
            "error": 0,
            "skipped": 0,
            "missing": 0,
        }

    @Slot()
    def run(self):
        self.artist_service = ArtistService()

        try:
            for offset, artist_id in enumerate(
                self.artist_ids,
                start=1,
            ):
                current = self.progress_offset + offset

                if self._should_cancel(current - 1):
                    return

                if self._should_pause(current - 1):
                    return

                self._check_artist(
                    artist_id,
                    current,
                    self.total_count,
                )

                self.progress_updated.emit(
                    current,
                    self.total_count,
                )

                if self._should_cancel(current):
                    return

                if self._should_pause(current):
                    return

                if offset < len(self.artist_ids):
                    self._rest_between_requests(current)

                    if self._should_cancel(current):
                        return

                    if self._should_pause(current):
                        return

                if offset % self.batch_size == 0 and current < self.total_count:
                    self._rest_between_batches(
                        current,
                        self.total_count,
                    )

                    if self._should_cancel(current):
                        return

                    if self._should_pause(current):
                        return

        except Exception as error:
            self._emit_failed(str(error))
            return

        self._emit_finished()

    def _check_artist(
        self,
        artist_id: int,
        index: int,
        total: int,
    ):
        try:
            artist = self.artist_service.get_artist(artist_id)

            if artist is None:
                raise ValueError("작가를 찾을 수 없습니다.")

            if self._should_skip_recent(artist):
                self._handle_skipped_recent(
                    artist=artist,
                    index=index,
                    total=total,
                )
                return

            previous_history = self.history_repo.get_previous_by_artist_id(
                artist_id
            )

            result = self.artist_service.check_artist_update(
                artist_id
            )
            artist = result.get("artist") or {}
            result_label = self._status_label(result)
            missing_count = result.get("missing_count", 0)

            comparison = self.history_repo.build_comparison(
                current_history={
                    "missing_count": missing_count,
                    "missing_ids": self._ids_to_text(
                        result.get("missing_ids")
                    ),
                },
                previous_history=previous_history,
            )

            self._update_summary(
                result_label,
                missing_count,
            )

            self.log_requested.emit(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "progress": f"{index}/{total}",
                    "result": result_label,
                    "artist_name": artist.get("artist_name", "-"),
                    "pixiv_id": artist.get("pixiv_id", "-"),
                    "local_count": result.get("local_count", "-"),
                    "pixiv_count": result.get("pixiv_count", "-"),
                    "missing_count": missing_count,
                    "missing_delta": comparison.get("missing_delta", 0),
                    "has_previous": comparison.get("has_previous", False),
                    "new_missing_count": comparison.get(
                        "new_missing_count",
                        0,
                    ),
                    "resolved_missing_count": comparison.get(
                        "resolved_missing_count",
                        0,
                    ),
                    "missing_ids": self._ids_to_text(
                        result.get("missing_ids")
                    ),
                    "new_missing_ids": comparison.get("new_missing_ids", ""),
                    "resolved_missing_ids": comparison.get(
                        "resolved_missing_ids",
                        "",
                    ),
                    "download_candidate_ids": self._ids_to_text(
                        result.get("download_candidate_ids")
                    ),
                    "status": result.get("status", "-"),
                }
            )
        except PixivRequestError as error:
            self._handle_error(
                artist_id=artist_id,
                index=index,
                total=total,
                message=error.to_display_text(),
            )

            if error.should_stop:
                self.cancel_event.set()
                self._emit_failed(error.to_display_text())
        except Exception as error:
            self._handle_error(
                artist_id=artist_id,
                index=index,
                total=total,
                message=f"[알 수 없는 오류] {error}",
            )

    def _should_skip_recent(
        self,
        artist: dict,
    ) -> bool:
        if not self.skip_recent:
            return False

        return self.artist_service.update_service.update_utils.was_recently_checked(
            artist
        )

    def _handle_skipped_recent(
        self,
        artist: dict,
        index: int,
        total: int,
    ):
        self.artist_service.update_service.save_skipped_recent_history(
            artist
        )
        self._update_summary("스킵", 0)

        self.log_requested.emit(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": f"{index}/{total}",
                "result": "스킵",
                "artist_name": artist.get("artist_name", "-"),
                "pixiv_id": artist.get("pixiv_id", "-"),
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": 0,
                "missing_delta": "-",
                "has_previous": False,
                "new_missing_count": "-",
                "resolved_missing_count": "-",
                "missing_ids": "",
                "new_missing_ids": "",
                "resolved_missing_ids": "",
                "download_candidate_ids": "",
                "status": "최근 1일 이내 확인한 작가",
            }
        )

    def _handle_error(
        self,
        artist_id: int,
        index: int,
        total: int,
        message: str,
    ):
        self.failed_artist_detected.emit(artist_id)
        self._update_summary("오류", 0)

        self.log_requested.emit(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": f"{index}/{total}",
                "result": "오류",
                "artist_name": f"artist_id={artist_id}",
                "pixiv_id": "-",
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": "-",
                "missing_delta": "-",
                "has_previous": False,
                "new_missing_count": "-",
                "resolved_missing_count": "-",
                "missing_ids": "",
                "new_missing_ids": "",
                "resolved_missing_ids": "",
                "download_candidate_ids": "",
                "status": message,
            }
        )

    def _update_summary(
        self,
        result_label: str,
        missing_count,
    ):
        self.summary["total"] += 1

        if result_label == "최신":
            self.summary["latest"] += 1
        elif result_label == "업데이트 필요":
            self.summary["need_update"] += 1
        elif result_label == "오류":
            self.summary["error"] += 1
        elif result_label == "스킵":
            self.summary["skipped"] += 1

        try:
            self.summary["missing"] += int(missing_count)
        except (TypeError, ValueError):
            pass

        self.summary_updated.emit(self.summary.copy())

    def _rest_between_requests(
        self,
        index: int,
    ):
        if self.request_interval_ms <= 0:
            return

        self._safe_sleep(self.request_interval_ms / 1000)

    def _rest_between_batches(
        self,
        index: int,
        total: int,
    ):
        if self.batch_rest_ms <= 0:
            return

        self._emit_info(
            index,
            total,
            "휴식",
            f"{self.batch_size}명 처리 완료. 잠시 대기합니다.",
        )
        self._safe_sleep(self.batch_rest_ms / 1000)

    def _safe_sleep(self, seconds: float):
        end_time = time.time() + seconds

        while time.time() < end_time:
            if self.cancel_event.is_set():
                return

            if self.pause_event.is_set():
                return

            time.sleep(0.2)

    def _should_cancel(
        self,
        current: int,
    ) -> bool:
        if not self.cancel_event.is_set():
            return False

        self._emit_info(
            current,
            self.total_count,
            "취소됨",
            "작업이 취소되었습니다.",
        )
        self.progress_updated.emit(
            0,
            self.total_count,
        )
        self._emit_finished()

        return True

    def _should_pause(
        self,
        current: int,
    ) -> bool:
        if not self.pause_event.is_set():
            return False

        self._emit_info(
            current,
            self.total_count,
            "일시정지",
            "현재 위치에서 작업이 일시정지되었습니다.",
        )
        self.progress_updated.emit(
            current,
            self.total_count,
        )
        self._emit_paused(
            current,
            self.total_count,
        )

        return True

    def _emit_info(
        self,
        current: int,
        total: int,
        result: str,
        message: str,
    ):
        self.log_requested.emit(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": f"{current}/{total}",
                "result": result,
                "artist_name": message,
                "pixiv_id": "-",
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": "-",
                "missing_delta": "-",
                "has_previous": False,
                "new_missing_count": "-",
                "resolved_missing_count": "-",
                "missing_ids": "",
                "new_missing_ids": "",
                "resolved_missing_ids": "",
                "download_candidate_ids": "",
                "status": "-",
            }
        )

    def _emit_paused(
        self,
        current: int,
        total: int,
    ):
        if self.has_finished or self.has_paused:
            return

        self.has_paused = True
        self.paused.emit(current, total)

    def _emit_finished(self):
        if self.has_finished or self.has_paused:
            return

        self.has_finished = True
        self.finished.emit()

    def _emit_failed(self, message: str):
        if self.has_finished or self.has_paused:
            return

        self.has_finished = True
        self.failed.emit(message)

    def _status_label(self, result: dict) -> str:
        result_label = result.get("result_label")

        if result_label:
            return result_label

        status = result.get("status")

        if status == "need_update":
            return "업데이트 필요"

        if status == "up_to_date":
            return "최신"

        if status == "unknown":
            return "미확인"

        if status == "error":
            return "오류"

        return "확인 완료"

    def _ids_to_text(
        self,
        values,
    ) -> str:
        if not values:
            return ""

        if isinstance(values, str):
            return values

        return ",".join(
            str(value).strip()
            for value in values
            if str(value).strip()
        )
