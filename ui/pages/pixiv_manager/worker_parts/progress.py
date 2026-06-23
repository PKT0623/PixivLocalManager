import time


class ProgressMixin:
    PIXIV_SYNC_UI_SIGNAL_ENABLED = False

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

        self._emit_direct_progress(current, total, message)

        elapsed = max(time.time() - self.started_at, 0.001)
        average = elapsed / max(current, 1)
        remain = max(total - current, 0)
        remain_seconds = int(average * remain)

        self.estimated_time_updated.emit(
            self._format_seconds(remain_seconds)
        )

    def _handle_rate_limit_status(
        self,
        message: str,
    ):
        if not self._should_emit_ui_signal():
            return

        self.progress_updated.emit(
            self.current_progress,
            self.current_total,
            message,
        )

    def _handle_sync_log(
        self,
        result: str,
        message: str,
    ):
        if not self._should_emit_ui_signal():
            return

        self.log_requested.emit(
            {
                "target": self.target_label,
                "result": result,
                "message": message,
                "new_count": 0,
                "duplicate_in_file_count": 0,
                "duplicate_existing_count": 0,
                "error_count": (
                    1
                    if result in ("실패", "세션 오류", "요청 제한")
                    else 0
                ),
            }
        )

    def _emit_direct_progress(
        self,
        current: int,
        total: int,
        message: str,
    ):
        self.current_progress = current
        self.current_total = total

        if not self._should_emit_ui_signal():
            return

        self.progress_updated.emit(current, total, message)

    def _emit_progress(
        self,
        index: int,
        total: int,
        started_at: float,
    ):
        self._emit_direct_progress(
            index,
            total,
            f"{index} / {total}",
        )

        elapsed = max(time.time() - started_at, 0.001)
        average = elapsed / index
        remain = max(total - index, 0)
        remain_seconds = int(average * remain)

        self.estimated_time_updated.emit(
            self._format_seconds(remain_seconds)
        )

    def _should_emit_ui_signal(self) -> bool:
        if getattr(self, "import_source", "") != "pixiv":
            return True

        return self.PIXIV_SYNC_UI_SIGNAL_ENABLED

    def _is_cancel_requested(self) -> bool:
        return self.cancel_requested

    def _format_seconds(
        self,
        seconds: int,
    ) -> str:
        if seconds <= 0:
            return "곧 완료"

        minutes = seconds // 60
        remain_seconds = seconds % 60

        if minutes <= 0:
            return f"약 {remain_seconds}초"

        return f"약 {minutes}분 {remain_seconds}초"
