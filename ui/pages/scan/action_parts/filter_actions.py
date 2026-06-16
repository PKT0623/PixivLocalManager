class ScanFilterActions:
    def apply_result_filter(self):
        result_filter = self.page.result_filter_combo.currentText()
        self.page.log_table.set_result_filter(result_filter)

    def apply_error_only_filter(self):
        self.page.log_table.set_error_only(
            self.page.error_only_checkbox.isChecked()
        )

    def apply_preview_filters(self):
        self.page.preview_table.set_filters(
            show_created_only=(
                self.page.preview_show_created_checkbox.isChecked()
            ),
            show_updated_only=(
                self.page.preview_show_updated_checkbox.isChecked()
            ),
            show_error_only=(
                self.page.preview_show_error_checkbox.isChecked()
            ),
            hide_unchanged=(
                self.page.preview_hide_unchanged_checkbox.isChecked()
            ),
        )

    def clear_scan_results(self):
        self.clear_resume_state()
        self.page.log_table.clear_log()
        self.page.preview_table.clear_preview()
        self.page.progress_section.reset()
        self.load_scan_history()
