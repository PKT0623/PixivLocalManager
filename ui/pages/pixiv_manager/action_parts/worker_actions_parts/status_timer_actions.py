from PySide6.QtCore import QTimer


class PixivManagerWorkerStatusTimerActionsMixin:
    def _start_pixiv_status_poll_timer(self):
        self._stop_pixiv_status_poll_timer()

        timer = QTimer(self.page)
        timer.setInterval(self.PIXIV_STATUS_POLL_INTERVAL_MS)
        timer.timeout.connect(self._update_pixiv_status_from_worker)

        self.page.pixiv_status_poll_timer = timer
        timer.start()

    def _stop_pixiv_status_poll_timer(self):
        timer = getattr(self.page, "pixiv_status_poll_timer", None)

        if timer is None:
            return

        timer.stop()
        timer.deleteLater()
        self.page.pixiv_status_poll_timer = None

    def _update_pixiv_status_from_worker(self):
        worker = self.page.worker

        if worker is None:
            return

        if getattr(worker, "import_source", "") != "pixiv":
            return

        current = int(getattr(worker, "current_progress", 0) or 0)
        total = int(getattr(worker, "current_total", 0) or 0)
        percent = self._calculate_percent(current, total)

        if total <= 0:
            self.page.status_label.setText("Pixiv 동기화 중...")
            return

        self.page.status_label.setText(
            f"Pixiv 동기화 중: {percent}% ({current} / {total})"
        )
