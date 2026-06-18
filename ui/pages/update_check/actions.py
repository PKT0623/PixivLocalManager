import csv
from datetime import datetime
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QThread, Slot

from app.services.pixiv_update_service import PixivUpdateService
from app.services.settings_service import SettingsService

from .worker import UpdateCheckWorker
from .worker_config import (
    MIN_UPDATE_CHECK_BATCH_REST_MS,
    MIN_UPDATE_CHECK_BATCH_SIZE,
    MIN_UPDATE_CHECK_REQUEST_INTERVAL_MS,
)


class UpdateCheckActions(QObject):
    def __init__(self, page):
        super().__init__(page)

        self.page = page
        self.cancel_event = None
        self.pause_event = None
        self.settings_service = SettingsService()
        self.pixiv_update_service = PixivUpdateService()

        self.current_artist_ids = []
        self.resume_artist_ids = []
        self.progress_offset = 0
        self.total_count = 0
        self.current_summary = None
        self.is_paused = False
        self.is_cancel_requested = False

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

        worker_thread.start()

    def pause_update_check(self):
        if self.pause_event is None:
            return

        self.pause_event.set()
        self.page.pause_button.setEnabled(False)
        self.page.resume_button.setEnabled(False)
        self.page.status_label.setText(
            "일시정지 요청을 보냈습니다. 현재 작가 완료 후 멈춥니다."
        )

    def cancel_update_check(self):
        if self.is_paused:
            self._cancel_paused_task()
            return

        if self.cancel_event is None:
            return

        self.is_cancel_requested = True
        self.cancel_event.set()
        self.resume_artist_ids = []
        self.progress_offset = 0
        self.is_paused = False

        self.page.cancel_button.setEnabled(False)
        self.page.pause_button.setEnabled(False)
        self.page.resume_button.setEnabled(False)
        self.page.status_label.setText(
            "중지 요청을 보냈습니다. 현재 작업 후 중지됩니다."
        )

    def _cancel_paused_task(self):
        total = self.total_count

        self.resume_artist_ids = []
        self.progress_offset = 0
        self.total_count = 0
        self.is_paused = False
        self.is_cancel_requested = False

        self.page.log_table.add_log_row(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": f"0/{total}",
                "result": "취소됨",
                "artist_name": "일시정지된 작업이 중지되었습니다.",
                "pixiv_id": "-",
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": "-",
                "missing_ids": "",
                "download_candidate_ids": "",
                "status": "-",
            }
        )

        self.update_progress(0, total)
        self.set_running_state(False)
        self.page.export_csv_button.setEnabled(
            self.page.log_table.rowCount() > 0
        )
        self.page.status_label.setText("업데이트 확인이 중지되었습니다.")
        self.page.load_artists()

    def test_phpsessid(self):
        phpsessid = self.settings_service.get_setting("pixiv_phpsessid")

        if not phpsessid:
            self.page.status_label.setText(
                "PHPSESSID가 설정되어 있지 않습니다."
            )
            return

        self.page.test_phpsessid_button.setEnabled(False)
        self.page.status_label.setText("PHPSESSID 연결 테스트 중...")

        result = self.pixiv_update_service.test_phpsessid(phpsessid)

        if result.get("success"):
            self.page.status_label.setText(
                "PHPSESSID 연결 테스트에 성공했습니다."
            )
        else:
            self.page.status_label.setText(
                f"PHPSESSID 연결 테스트 실패: {result.get('message')}"
            )

        self.page.test_phpsessid_button.setEnabled(True)

    def export_log_csv(self):
        if self.page.log_table.rowCount() == 0:
            self.page.status_label.setText("저장할 결과 로그가 없습니다.")
            return

        export_dir = Path("exports") / "update_logs"
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = export_dir / f"update_check_log_{timestamp}.csv"

        headers, rows = self.page.log_table.get_csv_data()

        with file_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

        self.page.status_label.setText(
            f"CSV 저장 완료: {file_path}"
        )

    @Slot(dict)
    def handle_summary_updated(self, summary: dict):
        self.current_summary = summary.copy()
        self.page.update_summary(summary)

    @Slot(int)
    def add_failed_artist_id(self, artist_id: int):
        if artist_id not in self.page.failed_artist_ids:
            self.page.failed_artist_ids.append(artist_id)

    @Slot(int, int)
    def handle_paused(self, current: int, total: int):
        self.progress_offset = current
        self.total_count = total
        self.resume_artist_ids = self.current_artist_ids[current:]
        self.is_paused = True

        self.page.resume_button.setEnabled(False)
        self.page.cancel_button.setEnabled(False)
        self.page.status_label.setText(
            f"업데이트 확인 일시정지 정리 중: {current} / {total}"
        )

    @Slot()
    def handle_finished(self):
        self.resume_artist_ids = []
        self.progress_offset = 0
        self.total_count = 0
        self.is_paused = False

        if self.is_cancel_requested:
            self.page.status_label.setText("업데이트 확인이 중지되었습니다.")
        else:
            self.page.status_label.setText("업데이트 확인이 완료되었습니다.")

        self.is_cancel_requested = False
        self.set_running_state(False)
        self.page.export_csv_button.setEnabled(
            self.page.log_table.rowCount() > 0
        )
        self.page.update_finished.emit()

    @Slot(str)
    def handle_failed(self, message: str):
        self.resume_artist_ids = []
        self.progress_offset = 0
        self.total_count = 0
        self.is_paused = False
        self.is_cancel_requested = False

        self.page.status_label.setText(message)
        self.set_running_state(False)
        self.page.export_csv_button.setEnabled(
            self.page.log_table.rowCount() > 0
        )
        self.page.update_finished.emit()

    @Slot()
    def cleanup_worker(self):
        self.page.worker = None
        self.page.worker_thread = None

        self.cancel_event = None
        self.pause_event = None

        if self.is_paused:
            self.page.status_label.setText(
                f"업데이트 확인 일시정지: "
                f"{self.progress_offset} / {self.total_count}"
            )
            self.set_paused_state()
        else:
            self.page.load_artists()

    def shutdown_worker(self):
        if self.cancel_event is not None:
            self.cancel_event.set()

        if self.pause_event is not None:
            self.pause_event.set()

        if self.page.worker_thread is None:
            return

        if self.page.worker_thread.isRunning():
            self.page.worker_thread.quit()
            self.page.worker_thread.wait(3000)

    @Slot(int, int)
    def update_progress(self, current: int, total: int):
        self.page.progress_bar.setRange(0, total)
        self.page.progress_bar.setValue(current)
        self.page.progress_bar.setFormat(f"{current} / {total}")

    def reset_progress(self, total: int):
        self.update_progress(0, total)
        self.page.status_label.setText(f"업데이트 확인 시작: {total}명")

    def set_running_state(self, is_running: bool):
        self.page.start_button.setEnabled(not is_running)
        self.page.pause_button.setEnabled(is_running)
        self.page.resume_button.setEnabled(False)
        self.page.cancel_button.setEnabled(is_running)

        self.page.select_all_button.setEnabled(not is_running)
        self.page.clear_selection_button.setEnabled(not is_running)
        self.page.select_unknown_button.setEnabled(not is_running)
        self.page.select_need_update_button.setEnabled(not is_running)
        self.page.select_failed_button.setEnabled(not is_running)
        self.page.skip_recent_checkbox.setEnabled(not is_running)
        self.page.test_phpsessid_button.setEnabled(not is_running)
        self.page.export_csv_button.setEnabled(
            not is_running and self.page.log_table.rowCount() > 0
        )
        self.page.request_interval_ms_input.setEnabled(not is_running)
        self.page.batch_size_input.setEnabled(not is_running)
        self.page.batch_rest_ms_input.setEnabled(not is_running)
        self.page.artist_table.setEnabled(not is_running)

    def set_paused_state(self):
        self.page.start_button.setEnabled(False)
        self.page.pause_button.setEnabled(False)
        self.page.resume_button.setEnabled(bool(self.resume_artist_ids))
        self.page.cancel_button.setEnabled(True)

        self.page.select_all_button.setEnabled(False)
        self.page.clear_selection_button.setEnabled(False)
        self.page.select_unknown_button.setEnabled(False)
        self.page.select_need_update_button.setEnabled(False)
        self.page.select_failed_button.setEnabled(False)
        self.page.skip_recent_checkbox.setEnabled(False)
        self.page.test_phpsessid_button.setEnabled(False)
        self.page.export_csv_button.setEnabled(
            self.page.log_table.rowCount() > 0
        )
        self.page.request_interval_ms_input.setEnabled(False)
        self.page.batch_size_input.setEnabled(False)
        self.page.batch_rest_ms_input.setEnabled(False)
        self.page.artist_table.setEnabled(False)

    def _is_worker_running(self) -> bool:
        return (
            self.page.worker_thread is not None
            and self.page.worker_thread.isRunning()
        )
