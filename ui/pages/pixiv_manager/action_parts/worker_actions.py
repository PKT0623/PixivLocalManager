from PySide6.QtCore import QThread, Qt

from ..worker import PixivImportWorker

from .worker_actions_parts import (
    PixivManagerWorkerLifecycleActionsMixin,
    PixivManagerWorkerResultActionsMixin,
    PixivManagerWorkerStateActionsMixin,
    PixivManagerWorkerStatusTimerActionsMixin,
)


class PixivManagerWorkerActions(
    PixivManagerWorkerLifecycleActionsMixin,
    PixivManagerWorkerResultActionsMixin,
    PixivManagerWorkerStatusTimerActionsMixin,
    PixivManagerWorkerStateActionsMixin,
):
    PIXIV_STATUS_POLL_INTERVAL_MS = 200

    def _start_import(
        self,
        target_type: str,
        file_type: str,
        import_source: str = "file",
        file_path: str = "",
        phpsessid: str = "",
        selected_items: list[dict] | None = None,
    ):
        if self._is_worker_running():
            self.page.status_label.setText(
                "이미 가져오기가 진행 중입니다."
            )
            return

        self._cleanup_finished_worker_refs()
        self._stop_pixiv_status_poll_timer()

        if import_source == "file" and not file_path:
            file_path = self._get_file_path()

            if not file_path:
                return

        self._set_import_running(True)

        self.page.progress_bar.setRange(0, 100)
        self.page.progress_bar.setValue(0)
        self.page.progress_bar.setFormat("0%")

        if import_source == "pixiv":
            self.page.status_label.setText("Pixiv 동기화 준비 중...")
        else:
            self.page.status_label.setText("가져오기 준비 중...")

        self._pending_worker_result = None
        self._pending_worker_error_message = ""

        worker_thread = QThread(self.page)
        worker = PixivImportWorker(
            target_type=target_type,
            file_type=file_type,
            file_path=file_path,
            import_source=import_source,
            phpsessid=phpsessid,
            selected_items=selected_items or [],
        )

        self.page.worker_thread = worker_thread
        self.page.worker = worker

        worker.moveToThread(worker_thread)

        worker_thread.started.connect(
            worker.run,
            Qt.ConnectionType.QueuedConnection,
        )

        worker.progress_updated.connect(
            self._handle_progress_updated,
            Qt.ConnectionType.QueuedConnection,
        )

        worker.finished.connect(
            lambda: self._capture_worker_result(worker),
            Qt.ConnectionType.DirectConnection,
        )
        worker.failed.connect(
            lambda: self._capture_worker_result(worker),
            Qt.ConnectionType.DirectConnection,
        )

        worker.finished.connect(
            worker_thread.quit,
            Qt.ConnectionType.QueuedConnection,
        )
        worker.failed.connect(
            worker_thread.quit,
            Qt.ConnectionType.QueuedConnection,
        )

        worker_thread.finished.connect(
            self._handle_worker_thread_finished,
            Qt.ConnectionType.QueuedConnection,
        )

        worker_thread.start()

        if import_source == "pixiv":
            self._start_pixiv_status_poll_timer()
