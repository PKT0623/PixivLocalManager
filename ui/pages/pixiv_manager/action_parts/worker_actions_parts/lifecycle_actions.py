from PySide6.QtCore import Slot


class PixivManagerWorkerLifecycleActionsMixin:
    def _capture_worker_result(
        self,
        worker,
    ):
        self._pending_worker_result = getattr(
            worker,
            "result_payload",
            None,
        )
        self._pending_worker_error_message = getattr(
            worker,
            "error_message",
            "",
        )

    @Slot(int, int, str)
    def _handle_progress_updated(
        self,
        current: int,
        total: int,
        message: str,
    ):
        worker = self.page.worker

        if worker is not None and getattr(worker, "import_source", "") == "pixiv":
            return

        percent = self._calculate_percent(current, total)

        self.page.progress_bar.setRange(0, 100)
        self.page.progress_bar.setValue(percent)

        if total <= 0:
            self.page.progress_bar.setFormat(f"{percent}%")
        else:
            self.page.progress_bar.setFormat(
                f"{percent}% ({current} / {total})"
            )

        if message:
            self.page.status_label.setText(message)

    @Slot()
    def _handle_worker_thread_finished(self):
        self._stop_pixiv_status_poll_timer()

        result = getattr(
            self,
            "_pending_worker_result",
            None,
        )
        error_message = getattr(
            self,
            "_pending_worker_error_message",
            "",
        )

        self._process_worker_result(
            result,
            error_message,
        )

        self.page.worker = None
        self.page.worker_thread = None
        self._pending_worker_result = None
        self._pending_worker_error_message = ""

    def _cleanup_finished_worker_refs(self):
        worker_thread = self.page.worker_thread

        if worker_thread is not None and not worker_thread.isRunning():
            self.page.worker = None
            self.page.worker_thread = None

    def shutdown_worker(self):
        self._stop_pixiv_status_poll_timer()

        if self.page.worker_thread is None:
            return

        if self._is_worker_running() and self.page.worker is not None:
            self.page.worker.request_cancel()

        if self.page.worker_thread.isRunning():
            self.page.worker_thread.quit()
            self.page.worker_thread.wait(3000)

        self.page.worker = None
        self.page.worker_thread = None
