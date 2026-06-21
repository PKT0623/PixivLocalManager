from PySide6.QtCore import QThread

from ...worker import ScanWorker


class ScanWorkerStartActions:
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

        self._connect_worker_signals(resume_payload)
        self.page.scan_thread.start()

    def _connect_worker_signals(
        self,
        resume_payload: dict | None,
    ):
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
