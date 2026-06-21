from PySide6.QtCore import Slot


class UpdateCheckWorkerHandlerActions:
    @Slot(dict)
    def handle_log_requested(self, row_data: dict):
        self.page.log_table.add_log_row(row_data)

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
        self.update_log_action_buttons()
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
        self.update_log_action_buttons()
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
