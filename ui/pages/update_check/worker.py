from threading import Event

from PySide6.QtCore import QObject, Signal

from app.database import ArtistUpdateHistoryRepository

from .worker_config import (
    DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
    DEFAULT_UPDATE_CHECK_BATCH_SIZE,
    DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
)
from .worker_parts import (
    UpdateCheckWorkerLogMixin,
    UpdateCheckWorkerPauseMixin,
    UpdateCheckWorkerRunMixin,
    UpdateCheckWorkerSleepMixin,
    UpdateCheckWorkerSummaryMixin,
)


class UpdateCheckWorker(
    QObject,
    UpdateCheckWorkerRunMixin,
    UpdateCheckWorkerSummaryMixin,
    UpdateCheckWorkerPauseMixin,
    UpdateCheckWorkerSleepMixin,
    UpdateCheckWorkerLogMixin,
):
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

        self.request_interval_ms = max(
            0,
            int(request_interval_ms),
        )
        self.batch_size = max(
            1,
            int(batch_size),
        )
        self.batch_rest_ms = max(
            0,
            int(batch_rest_ms),
        )

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
