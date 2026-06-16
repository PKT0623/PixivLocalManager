from datetime import datetime

from PySide6.QtCore import QThread

from ..worker import ScanWorker


class ScanWorkerActions:
    def start_preview(self):
        folder_path = self.page.folder_section.folder_path_input.text().strip()

        if not folder_path:
            self.page.log_table.add_info_log("오류: 먼저 폴더를 선택하세요.")
            return

        self.clear_resume_state()

        self.page.settings_service.set_setting(
            "last_scan_folder",
            folder_path,
        )

        self._start_worker(
            folder_path=folder_path,
            target_folder_paths=None,
            clear_log=True,
            preview_mode=True,
            resume_payload=None,
        )

    def start_scan(self):
        folder_path = self.page.folder_section.folder_path_input.text().strip()

        if not folder_path:
            self.page.log_table.add_info_log("오류: 먼저 폴더를 선택하세요.")
            return

        self.clear_resume_state()

        self.page.settings_service.set_setting(
            "last_scan_folder",
            folder_path,
        )

        self._start_worker(
            folder_path=folder_path,
            target_folder_paths=None,
            clear_log=True,
            preview_mode=False,
            resume_payload=None,
        )

    def start_selected_preview_items_scan(self):
        folder_paths = self.page.preview_table.get_selected_folder_paths()

        if not folder_paths:
            self.page.log_table.add_info_log("선택된 등록 대상이 없습니다.")
            return

        self.clear_resume_state()

        root_folder = self.page.folder_section.folder_path_input.text().strip()

        if not root_folder:
            root_folder = str(folder_paths[0])

        self.page.log_table.add_info_log(
            f"선택 항목 등록 시작: {len(folder_paths)}개"
        )

        self._start_worker(
            folder_path=root_folder,
            target_folder_paths=folder_paths,
            clear_log=True,
            preview_mode=False,
            resume_payload=None,
        )

    def pause_scan(self):
        if self.page.scan_worker is None:
            self.page.log_table.add_info_log("일시정지할 스캔이 없습니다.")
            return

        self.page.scan_worker.request_pause()
        self.page.progress_section.update_scan_state(
            "현재 작업 완료 후 일시정지 예정"
        )
        self.page.folder_section.pause_button.setEnabled(False)
        self.page.log_table.add_info_log(
            "일시정지 요청: 현재 작업 완료 후 정지합니다."
        )

    def resume_scan(self):
        if not self.resume_payload:
            self.page.log_table.add_info_log("이어갈 스캔이 없습니다.")
            return

        if self.page.scan_thread is not None:
            self.page.log_table.add_info_log(
                "스캔 정리 중입니다. 잠시 후 다시 시도하세요."
            )
            return

        folder_paths = self.resume_payload.get("remaining_folder_paths", [])
        folder_path = self.resume_payload.get("root_folder_path", "")
        preview_mode = bool(self.resume_payload.get("preview_mode", False))

        if not folder_paths:
            self.page.log_table.add_info_log("이어갈 남은 항목이 없습니다.")
            self.clear_resume_state()
            return

        self.page.log_table.add_info_log(
            f"이어서 스캔 시작: 남은 항목 {len(folder_paths)}개"
        )

        payload = dict(self.resume_payload)

        self._start_worker(
            folder_path=folder_path,
            target_folder_paths=folder_paths,
            clear_log=False,
            preview_mode=preview_mode,
            resume_payload=payload,
        )

    def stop_scan(self):
        if self.page.scan_worker is None:
            self.page.log_table.add_info_log("중지할 스캔이 없습니다.")
            return

        self.page.scan_worker.request_stop()
        self.clear_resume_state()
        self.page.progress_section.update_scan_state(
            "중지 요청됨"
        )
        self.page.folder_section.stop_button.setEnabled(False)
        self.page.folder_section.pause_button.setEnabled(False)
        self.page.log_table.add_info_log(
            "스캔 중지 요청: 현재 작업 완료 후 중단합니다."
        )

    def clear_resume_state(self):
        self.resume_payload = None
        self.page.folder_section.resume_button.setEnabled(False)

    def _start_worker(
        self,
        folder_path: str,
        target_folder_paths: list[str] | None,
        clear_log: bool,
        preview_mode: bool,
        resume_payload: dict | None,
    ):
        if self.page.scan_thread is not None:
            self.page.log_table.add_info_log("이미 스캔이 진행 중입니다.")
            return

        self.current_run_preview_mode = preview_mode
        self.set_scanning_state(True)
        self.page.progress_section.reset()
        self.load_scan_history()

        if resume_payload:
            self._restore_resume_progress_state(resume_payload)

        if clear_log:
            self.page.log_table.clear_log()

        if preview_mode:
            if clear_log:
                self.page.preview_table.clear_preview()

            if resume_payload is None:
                self.page.log_table.add_info_log(
                    f"스캔 미리보기 시작: {folder_path}"
                )
        else:
            if resume_payload is None:
                self.page.log_table.add_info_log(f"스캔 시작: {folder_path}")

        self.page.scan_thread = QThread()
        self.page.scan_worker = ScanWorker(
            folder_path,
            target_folder_paths=target_folder_paths,
            preview_mode=preview_mode,
            resume_payload=resume_payload,
        )
        self.page.scan_worker.moveToThread(self.page.scan_thread)

        self.page.scan_thread.started.connect(
            self.page.scan_worker.run
        )
        self.page.scan_worker.log_message_requested.connect(
            self.page.log_table.add_info_log
        )
        self.page.scan_worker.scan_result_requested.connect(
            self.page.log_table.add_log_row
        )
        self.page.scan_worker.preview_result_requested.connect(
            self.page.preview_table.append_preview_rows
            if resume_payload
            else self.page.preview_table.set_preview_rows
        )
        self.page.scan_worker.preview_summary_updated.connect(
            self.page.progress_section.update_summary
        )
        self.page.scan_worker.progress_updated.connect(
            self.page.progress_section.update_progress
        )
        self.page.scan_worker.current_folder_changed.connect(
            self.page.progress_section.update_current_folder
        )
        self.page.scan_worker.target_count_changed.connect(
            self.page.progress_section.update_target_count
        )
        self.page.scan_worker.summary_updated.connect(
            self.page.progress_section.update_summary
        )
        self.page.scan_worker.statistics_updated.connect(
            self.page.progress_section.update_statistics
        )
        self.page.scan_worker.runtime_info_updated.connect(
            self.page.progress_section.update_runtime_info
        )
        self.page.scan_worker.paused.connect(
            self.handle_scan_paused
        )
        self.page.scan_worker.stopped.connect(
            self.handle_scan_stopped
        )
        self.page.scan_worker.failed.connect(
            self.handle_scan_failed
        )
        self.page.scan_worker.finished.connect(
            self.handle_scan_finished
        )

        self.page.scan_worker.finished.connect(
            self.page.scan_thread.quit
        )
        self.page.scan_worker.failed.connect(
            self.page.scan_thread.quit
        )
        self.page.scan_worker.paused.connect(
            self.page.scan_thread.quit
        )
        self.page.scan_worker.stopped.connect(
            self.page.scan_thread.quit
        )
        self.page.scan_thread.finished.connect(
            self.cleanup_scan_thread
        )

        self.page.scan_thread.start()

    def _restore_resume_progress_state(
        self,
        resume_payload: dict,
    ):
        self.page.progress_section.update_scan_state("재개 중")

        summary = resume_payload.get("summary", {})
        statistics = resume_payload.get("statistics", {})
        current = int(resume_payload.get("completed_count", 0) or 0)
        total = int(resume_payload.get("total_count", 0) or 0)

        self.page.progress_section.update_summary(summary)
        self.page.progress_section.update_statistics(statistics)
        self.page.progress_section.update_progress(current, total)

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

    def cleanup_scan_thread(self):
        self.page.scan_worker = None
        self.page.scan_thread = None

        if self.resume_payload:
            self.page.folder_section.resume_button.setEnabled(True)

    def set_scanning_state(self, is_scanning: bool):
        self.page.folder_section.scan_button.setEnabled(not is_scanning)
        self.page.folder_section.preview_button.setEnabled(not is_scanning)
        self.page.folder_section.folder_select_button.setEnabled(
            not is_scanning
        )

        self.page.folder_section.pause_button.setEnabled(is_scanning)
        self.page.folder_section.stop_button.setEnabled(is_scanning)
        self.page.folder_section.resume_button.setEnabled(
            (not is_scanning)
            and bool(self.resume_payload)
            and self.page.scan_thread is None
        )

        self.page.clear_log_button.setEnabled(not is_scanning)
        self.page.retry_failed_button.setEnabled(not is_scanning)
        self.page.clear_failed_button.setEnabled(not is_scanning)
        self.page.export_failed_csv_button.setEnabled(not is_scanning)
        self.page.export_all_csv_button.setEnabled(not is_scanning)

        self.page.preview_scan_selected_button.setEnabled(not is_scanning)
        self.page.preview_select_all_button.setEnabled(not is_scanning)
        self.page.preview_clear_selection_button.setEnabled(not is_scanning)
        self.page.preview_exclude_selected_button.setEnabled(not is_scanning)
        self.page.preview_keep_selected_button.setEnabled(not is_scanning)
        self.page.preview_exclude_error_button.setEnabled(not is_scanning)
        self.page.preview_export_csv_button.setEnabled(not is_scanning)

        self.page.preview_show_created_checkbox.setEnabled(not is_scanning)
        self.page.preview_show_updated_checkbox.setEnabled(not is_scanning)
        self.page.preview_show_error_checkbox.setEnabled(not is_scanning)
        self.page.preview_hide_unchanged_checkbox.setEnabled(not is_scanning)

        if is_scanning:
            self.page.progress_section.update_scan_state("진행 중")
            self.page.folder_section.scan_button.setText("스캔 중...")
        else:
            self.page.folder_section.scan_button.setText("스캔 및 등록")

    def set_paused_state(self):
        self.page.folder_section.scan_button.setEnabled(True)
        self.page.folder_section.preview_button.setEnabled(True)
        self.page.folder_section.folder_select_button.setEnabled(True)

        self.page.folder_section.pause_button.setEnabled(False)
        self.page.folder_section.stop_button.setEnabled(False)
        self.page.folder_section.resume_button.setEnabled(False)

        self.page.clear_log_button.setEnabled(True)
        self.page.retry_failed_button.setEnabled(True)
        self.page.clear_failed_button.setEnabled(True)
        self.page.export_failed_csv_button.setEnabled(True)
        self.page.export_all_csv_button.setEnabled(True)

        self.page.preview_scan_selected_button.setEnabled(True)
        self.page.preview_select_all_button.setEnabled(True)
        self.page.preview_clear_selection_button.setEnabled(True)
        self.page.preview_exclude_selected_button.setEnabled(True)
        self.page.preview_keep_selected_button.setEnabled(True)
        self.page.preview_exclude_error_button.setEnabled(True)
        self.page.preview_export_csv_button.setEnabled(True)

        self.page.preview_show_created_checkbox.setEnabled(True)
        self.page.preview_show_updated_checkbox.setEnabled(True)
        self.page.preview_show_error_checkbox.setEnabled(True)
        self.page.preview_hide_unchanged_checkbox.setEnabled(True)

        self.page.folder_section.scan_button.setText("스캔 및 등록")
