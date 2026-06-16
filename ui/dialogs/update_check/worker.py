import random
import time
from datetime import datetime

from PySide6.QtCore import QObject, Signal

from app.services.artist import ArtistService

from .worker_config import (
    BATCH_SIZE,
    MAX_BATCH_REST_SECONDS,
    MAX_WAIT_SECONDS,
    MIN_BATCH_REST_SECONDS,
    MIN_WAIT_SECONDS,
)


class UpdateCheckWorker(QObject):
    log_requested = Signal(dict)
    progress_updated = Signal(int, int)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, artist_ids: list[int]):
        super().__init__()

        self.artist_ids = artist_ids
        self.artist_service = ArtistService()
        self.is_cancelled = False

    def run(self):
        total = len(self.artist_ids)

        try:
            for index, artist_id in enumerate(
                self.artist_ids,
                start=1,
            ):
                if self.is_cancelled:
                    self._emit_info(
                        index,
                        total,
                        "취소됨",
                        "작업이 취소되었습니다.",
                    )
                    break

                if index > 1:
                    self._safe_sleep(
                        random.uniform(
                            MIN_WAIT_SECONDS,
                            MAX_WAIT_SECONDS,
                        )
                    )

                try:
                    result = self.artist_service.check_artist_update(
                        artist_id
                    )
                    artist = result.get("artist") or {}

                    self.log_requested.emit(
                        {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "progress": f"{index}/{total}",
                            "result": self._status_label(result),
                            "artist_name": artist.get("artist_name", "-"),
                            "pixiv_id": artist.get("pixiv_id", "-"),
                            "local_count": result.get("local_count", "-"),
                            "pixiv_count": result.get("pixiv_count", "-"),
                            "missing_count": result.get("missing_count", "-"),
                            "status": result.get("status", "-"),
                        }
                    )
                except Exception as error:
                    error_message = str(error)

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
                            "status": error_message,
                        }
                    )

                    if (
                        "HTTP 403" in error_message
                        or "HTTP 429" in error_message
                    ):
                        self.failed.emit(
                            "Pixiv 요청 제한 가능성이 있어 작업을 중단했습니다."
                        )
                        return

                self.progress_updated.emit(
                    index,
                    total,
                )

                if index % BATCH_SIZE == 0 and index < total:
                    rest_seconds = random.uniform(
                        MIN_BATCH_REST_SECONDS,
                        MAX_BATCH_REST_SECONDS,
                    )
                    self._emit_info(
                        index,
                        total,
                        "휴식",
                        f"{BATCH_SIZE}명 처리 완료. 잠시 대기합니다.",
                    )
                    self._safe_sleep(rest_seconds)

        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit()

    def cancel(self):
        self.is_cancelled = True

    def _safe_sleep(self, seconds: float):
        end_time = time.time() + seconds

        while time.time() < end_time:
            if self.is_cancelled:
                return

            time.sleep(0.5)

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
                "status": "-",
            }
        )

    def _status_label(self, result: dict) -> str:
        status = result.get("status")

        if status == "need_update":
            return "업데이트 필요"

        if status == "up_to_date":
            return "최신"

        if status == "unknown":
            return "미확인"

        return "확인 완료"
