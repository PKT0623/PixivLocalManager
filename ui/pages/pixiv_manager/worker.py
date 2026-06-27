from PySide6.QtCore import QObject, Signal, Slot

from .worker_parts import (
    FileImportMixin,
    PixivSyncMixin,
    ProgressMixin,
    ResultBuilderMixin,
)


class PixivImportWorker(
    QObject,
    FileImportMixin,
    PixivSyncMixin,
    ProgressMixin,
    ResultBuilderMixin,
):
    progress_updated = Signal(int, int, str)
    log_requested = Signal(object)
    finished = Signal()
    failed = Signal()

    def __init__(
        self,
        target_type: str,
        file_type: str = "",
        file_path: str = "",
        import_source: str = "file",
        phpsessid: str = "",
        selected_items: list[dict] | None = None,
    ):
        QObject.__init__(self)

        self.target_type = target_type
        self.file_type = file_type
        self.file_path = file_path
        self.import_source = import_source
        self.phpsessid = phpsessid
        self.selected_items = selected_items or []

        self.started_at = 0.0
        self.target_label = self._get_target_label(target_type)

        self.current_progress = 0
        self.current_total = 0
        self.cancel_requested = False

        self.result_payload = None
        self.error_message = ""

        self._init_progress_state()

    @Slot()
    def run(self):
        try:
            if self.import_source == "pixiv":
                result = self._import_from_pixiv()
            elif self.target_type == "follow":
                result = self._import_follow()
            else:
                result = self._import_bookmark()

            self.result_payload = result
            self.error_message = ""

            self.finished.emit()
        except Exception as error:
            self.result_payload = None
            self.error_message = f"{type(error).__name__}: {error}"

            self.failed.emit()

    @Slot()
    def request_cancel(self):
        self.cancel_requested = True
