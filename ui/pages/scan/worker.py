from PySide6.QtCore import QObject, Signal

from app.services.artist import ArtistService
from app.services.artwork_status_service import ArtworkStatusService
from app.services.scan import FolderScanService

from .folder_scanner import FolderScanner
from .worker_parts import (
    ControlHandlerMixin,
    PreviewBuilderMixin,
    PreviewRunnerMixin,
    ResultBuilderMixin,
    RuntimeUtilsMixin,
    ScanRunnerMixin,
    StateManagerMixin,
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
    StateManagerMixin,
    ControlHandlerMixin,
    PreviewRunnerMixin,
    ScanRunnerMixin,
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
