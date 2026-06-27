class ProgressMixin:
    PIXIV_SYNC_UI_SIGNAL_ENABLED = True
    PROGRESS_PERCENT_STEP = 1

    def _init_progress_state(self) -> None:
        self._last_emitted_percent = -1

    def _handle_sync_progress(
        self,
        current: int,
        total: int,
        message: str,
    ):
        self.current_progress = current
        self.current_total = total

        if not self._should_emit_ui_signal():
            return

        self._emit_percent_progress(
            current=current,
            total=total,
            message=message,
            force=False,
        )

    def _handle_rate_limit_status(
        self,
        message: str,
    ):
        if not self._should_emit_ui_signal():
            return

        self._emit_percent_progress(
            current=self.current_progress,
            total=self.current_total,
            message=message,
            force=True,
        )

    def _handle_sync_log(
        self,
        result: str,
        message: str,
    ):
        return

    def _emit_direct_progress(
        self,
        current: int,
        total: int,
        message: str,
    ):
        self._emit_percent_progress(
            current=current,
            total=total,
            message=message,
            force=True,
        )

    def _emit_progress(
        self,
        index: int,
        total: int,
        started_at=None,
    ):
        self._emit_percent_progress(
            current=index,
            total=total,
            message="가져오기 진행 중...",
            force=False,
        )

    def _emit_percent_progress(
        self,
        current: int,
        total: int,
        message: str,
        force: bool = False,
    ):
        self.current_progress = current
        self.current_total = total

        percent = self._calculate_percent(current, total)

        if not force and not self._should_emit_percent(percent):
            return

        self._last_emitted_percent = percent
        self.progress_updated.emit(current, total, message)

    def _should_emit_percent(
        self,
        percent: int,
    ) -> bool:
        if percent <= 0 and self._last_emitted_percent < 0:
            return True

        if percent >= 100:
            return self._last_emitted_percent != 100

        if percent == self._last_emitted_percent:
            return False

        return percent - self._last_emitted_percent >= self.PROGRESS_PERCENT_STEP

    def _calculate_percent(
        self,
        current: int,
        total: int,
    ) -> int:
        if total <= 0:
            return 0

        safe_current = min(max(current, 0), total)
        return int(safe_current * 100 / total)

    def _should_emit_ui_signal(self) -> bool:
        if getattr(self, "import_source", "") != "pixiv":
            return True

        return self.PIXIV_SYNC_UI_SIGNAL_ENABLED

    def _is_cancel_requested(self) -> bool:
        return self.cancel_requested
