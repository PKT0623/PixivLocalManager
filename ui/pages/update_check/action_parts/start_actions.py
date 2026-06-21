from datetime import datetime
from threading import Event

from PySide6.QtCore import QThread

from ..worker import UpdateCheckWorker
from ..worker_config import (
    MIN_UPDATE_CHECK_BATCH_REST_MS,
    MIN_UPDATE_CHECK_BATCH_SIZE,
    MIN_UPDATE_CHECK_REQUEST_INTERVAL_MS,
)


class UpdateCheckStartActions:
    def start_update_check(self):
        if self._is_worker_running():
            self.page.status_label.setText(
                "이미 업데이트 확인이 진행 중입니다."
            )
            return

        artist_ids = self.page.selection_actions.get_selected_artist_ids()

        if not artist_ids:
            self.page.status_label.setText("업데이트 확인 대상이 없습니다.")
            return

        self.current_artist_ids = artist_ids
        self.resume_artist_ids = []
        self.progress_offset = 0
        self.total_count = len(artist_ids)
        self.current_summary = None
        self.is_paused = False
        self.is_cancel_requested = False

        self.page.failed_artist_ids = []
        self.page.reset_summary()
        self.page.log_table.clear_logs()

        self._start_worker(
            artist_ids=artist_ids,
            progress_offset=0,
            total_count=self.total_count,
            reset_progress=True,
        )

    def resume_update_check(self):
        if self._is_worker_running():
            self.page.status_label.setText(
                "이전 작업을 정리 중입니다. 잠시 후 다시 눌러주세요."
            )
            return

        if not self.resume_artist_ids:
            self.page.status_label.setText("재개할 작업이 없습니다.")
            return

        self.is_paused = False
        self.is_cancel_requested = False

        self.page.log_table.add_log_row(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": f"{self.progress_offset}/{self.total_count}",
                "result": "재개",
                "artist_name": "일시정지된 작업을 재개합니다.",
                "pixiv_id": "-",
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": "-",
                "missing_ids": "",
                "download_candidate_ids": "",
                "status": "-",
            }
        )

        self._start_worker(
            artist_ids=self.resume_artist_ids,
            progress_offset=self.progress_offset,
            total_count=self.total_count,
            reset_progress=False,
        )

    def _start_worker(
        self,
        artist_ids: list[int],
        progress_offset: int,
        total_count: int,
        reset_progress: bool,
    ):
        self.cancel_event = Event()
        self.pause_event = Event()

        self.set_running_state(True)
        self.page.export_csv_button.setEnabled(False)

        if reset_progress:
            self.reset_progress(total_count)
        else:
            self.update_progress(progress_offset, total_count)
            self.page.status_label.setText(
                f"업데이트 확인 재개: {progress_offset} / {total_count}"
            )

        request_interval_ms = max(
            MIN_UPDATE_CHECK_REQUEST_INTERVAL_MS,
            self.page.get_request_interval_ms(),
        )
        batch_size = max(
            MIN_UPDATE_CHECK_BATCH_SIZE,
            self.page.get_batch_size(),
        )
        batch_rest_ms = max(
            MIN_UPDATE_CHECK_BATCH_REST_MS,
            self.page.get_batch_rest_ms(),
        )

        worker_thread = QThread()
        worker = UpdateCheckWorker(
            artist_ids=artist_ids,
            cancel_event=self.cancel_event,
            pause_event=self.pause_event,
            skip_recent=self.page.skip_recent_checkbox.isChecked(),
            progress_offset=progress_offset,
            total_count=total_count,
            summary=self.current_summary,
            request_interval_ms=request_interval_ms,
            batch_size=batch_size,
            batch_rest_ms=batch_rest_ms,
        )

        self.page.worker_thread = worker_thread
        self.page.worker = worker

        worker.moveToThread(worker_thread)
        self._connect_worker_signals(worker_thread, worker)
        worker_thread.start()

    def _connect_worker_signals(
        self,
        worker_thread: QThread,
        worker: UpdateCheckWorker,
    ):
        worker_thread.started.connect(worker.run)

        worker.log_requested.connect(self.page.log_table.add_log_row)
        worker.progress_updated.connect(self.update_progress)
        worker.summary_updated.connect(self.handle_summary_updated)
        worker.failed_artist_detected.connect(self.add_failed_artist_id)
        worker.paused.connect(self.handle_paused)
        worker.finished.connect(self.handle_finished)
        worker.failed.connect(self.handle_failed)

        worker.paused.connect(worker_thread.quit)
        worker.finished.connect(worker_thread.quit)
        worker.failed.connect(worker_thread.quit)

        worker.paused.connect(worker.deleteLater)
        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)

        worker_thread.finished.connect(worker_thread.deleteLater)
        worker_thread.finished.connect(self.cleanup_worker)
