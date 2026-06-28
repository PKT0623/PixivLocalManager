class PixivManagerWorkerStateActionsMixin:
    def _set_import_running(
        self,
        is_running: bool,
    ):
        self.page.import_file_button.setEnabled(not is_running)
        self.page.browse_file_button.setEnabled(not is_running)
        self.page.import_target_combo.setEnabled(not is_running)
        self.page.import_file_type_combo.setEnabled(not is_running)
        self.page.refresh_button.setEnabled(not is_running)
        self.page.cancel_import_button.setEnabled(is_running)

        if hasattr(self.page, "pixiv_follow_button"):
            self.page.pixiv_follow_button.setEnabled(not is_running)

        if hasattr(self.page, "pixiv_bookmark_button"):
            self.page.pixiv_bookmark_button.setEnabled(not is_running)

    def _is_worker_running(self) -> bool:
        return (
            self.page.worker_thread is not None
            and self.page.worker_thread.isRunning()
        )

    def _calculate_percent(
        self,
        current: int,
        total: int,
    ) -> int:
        if total <= 0:
            return 0

        safe_current = min(max(current, 0), total)
        return int(safe_current * 100 / total)
