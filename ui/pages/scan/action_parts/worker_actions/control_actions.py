class ScanWorkerControlActions:
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
