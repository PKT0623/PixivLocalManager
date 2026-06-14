from PySide6.QtCore import QThread

from .utils import exclude_recently_checked
from .worker import UpdateCheckWorker


class UpdateCheckActions:
    def __init__(self, dialog):
        self.dialog = dialog

    def start_update_check(self):
        artist_ids = self.dialog.selection_actions.get_selected_artist_ids()

        if self.dialog.skip_recent_checkbox.isChecked():
            artist_ids = exclude_recently_checked(
                self.dialog.artists,
                artist_ids,
            )

        if not artist_ids:
            self.dialog.status_label.setText("업데이트 확인 대상이 없습니다.")
            return

        self.set_running_state(True)
        self.reset_progress(len(artist_ids))
        self.dialog.log_table.setRowCount(0)

        self.dialog.worker_thread = QThread()
        self.dialog.worker = UpdateCheckWorker(artist_ids)
        self.dialog.worker.moveToThread(self.dialog.worker_thread)

        self.dialog.worker_thread.started.connect(
            self.dialog.worker.run
        )
        self.dialog.worker.log_requested.connect(
            self.dialog.log_table.add_log_row
        )
        self.dialog.worker.progress_updated.connect(
            self.update_progress
        )
        self.dialog.worker.finished.connect(
            self.handle_finished
        )
        self.dialog.worker.failed.connect(
            self.handle_failed
        )

        self.dialog.worker.finished.connect(
            self.dialog.worker_thread.quit
        )
        self.dialog.worker.failed.connect(
            self.dialog.worker_thread.quit
        )
        self.dialog.worker_thread.finished.connect(
            self.cleanup_worker
        )

        self.dialog.worker_thread.start()

    def cancel_update_check(self):
        if self.dialog.worker is not None:
            self.dialog.worker.cancel()

        self.dialog.status_label.setText("취소 요청을 보냈습니다.")

    def handle_finished(self):
        self.dialog.status_label.setText("업데이트 확인이 완료되었습니다.")
        self.set_running_state(False)
        self.dialog.update_finished.emit()

    def handle_failed(self, message: str):
        self.dialog.status_label.setText(message)
        self.set_running_state(False)
        self.dialog.update_finished.emit()

    def cleanup_worker(self):
        if self.dialog.worker is not None:
            self.dialog.worker.deleteLater()
            self.dialog.worker = None

        if self.dialog.worker_thread is not None:
            self.dialog.worker_thread.deleteLater()
            self.dialog.worker_thread = None

    def reset_progress(self, total: int):
        self.dialog.progress_bar.setRange(0, total)
        self.dialog.progress_bar.setValue(0)
        self.dialog.progress_bar.setFormat(f"0 / {total}")
        self.dialog.status_label.setText(f"업데이트 확인 시작: {total}명")

    def update_progress(self, current: int, total: int):
        self.dialog.progress_bar.setRange(0, total)
        self.dialog.progress_bar.setValue(current)
        self.dialog.progress_bar.setFormat(f"{current} / {total}")

    def set_running_state(self, is_running: bool):
        self.dialog.start_button.setEnabled(not is_running)
        self.dialog.cancel_button.setEnabled(is_running)

        self.dialog.select_all_button.setEnabled(not is_running)
        self.dialog.clear_selection_button.setEnabled(not is_running)
        self.dialog.select_unknown_button.setEnabled(not is_running)
        self.dialog.select_need_update_button.setEnabled(not is_running)
        self.dialog.skip_recent_checkbox.setEnabled(not is_running)
        self.dialog.artist_table.setEnabled(not is_running)
