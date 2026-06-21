from PySide6.QtCore import Slot


class UpdateCheckUIStateActions:
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
