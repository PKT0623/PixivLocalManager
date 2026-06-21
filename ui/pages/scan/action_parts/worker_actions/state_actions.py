class ScanWorkerStateActions:
    def clear_resume_state(self):
        self.resume_payload = None
        self.page.folder_section.resume_button.setEnabled(False)

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
