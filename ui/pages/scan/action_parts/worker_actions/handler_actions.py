from datetime import datetime


class ScanWorkerHandlerActions:
    def handle_scan_finished(
        self,
        result: dict,
    ):
        self.clear_resume_state()

        if self.current_run_preview_mode:
            self.apply_preview_filters()
            self.page.progress_section.update_scan_state("미리보기 완료")
            self.set_scanning_state(False)
            return

        self._save_scan_result(result)
        self.load_scan_history()
        self.page.progress_section.update_scan_state("완료")
        self.set_scanning_state(False)

    def handle_scan_paused(
        self,
        payload: dict,
    ):
        self.resume_payload = payload

        remaining_count = len(payload.get("remaining_folder_paths", []) or [])

        self.page.progress_section.update_scan_state(
            f"일시정지됨 / 재개 가능 {remaining_count}개"
        )
        self.page.log_table.add_info_log(
            f"스캔 일시정지: 남은 항목 {remaining_count}개"
        )
        self.set_paused_state()
        self.page.folder_section.resume_button.setEnabled(False)

    def handle_scan_stopped(
        self,
        payload: dict,
    ):
        self.clear_resume_state()

        stopped_count = int(payload.get("completed_count", 0) or 0)
        total_count = int(payload.get("total_count", 0) or 0)

        self.page.progress_section.reset_progress_only()
        self.page.progress_section.update_scan_state("중단됨")
        self.page.log_table.add_info_log(
            f"스캔 중단: 처리 {stopped_count}/{total_count}"
        )
        self.set_scanning_state(False)

    def handle_scan_failed(self, error_message: str):
        self.clear_resume_state()

        self.page.log_table.add_log_row(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": "-",
                "result": "실패",
                "artist_id": None,
                "artist_name": "스캔 작업 오류",
                "pixiv_id": "-",
                "artwork_count": "-",
                "file_count": "-",
                "update_status": "error",
                "folder_path": (
                    self.page.folder_section.folder_path_input.text().strip()
                ),
                "error_message": error_message,
            }
        )
        self.page.progress_section.update_scan_state("실패")
        self.set_scanning_state(False)
