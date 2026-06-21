from datetime import datetime


class UpdateCheckControlActions:
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
