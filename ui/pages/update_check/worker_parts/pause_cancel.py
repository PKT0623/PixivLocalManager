class UpdateCheckWorkerPauseMixin:
    def _should_cancel(
        self,
        current: int,
    ) -> bool:
        if not self.cancel_event.is_set():
            return False

        self._emit_info(
            current,
            self.total_count,
            "취소됨",
            "작업이 취소되었습니다.",
        )

        self.progress_updated.emit(
            0,
            self.total_count,
        )

        self._emit_finished()

        return True

    def _should_pause(
        self,
        current: int,
    ) -> bool:
        if not self.pause_event.is_set():
            return False

        self._emit_info(
            current,
            self.total_count,
            "일시정지",
            "현재 위치에서 작업이 일시정지되었습니다.",
        )

        self.progress_updated.emit(
            current,
            self.total_count,
        )

        self._emit_paused(
            current,
            self.total_count,
        )

        return True

    def _emit_paused(
        self,
        current: int,
        total: int,
    ):
        if self.has_finished or self.has_paused:
            return

        self.has_paused = True
        self.paused.emit(
            current,
            total,
        )

    def _emit_finished(self):
        if self.has_finished or self.has_paused:
            return

        self.has_finished = True
        self.finished.emit()

    def _emit_failed(
        self,
        message: str,
    ):
        if self.has_finished or self.has_paused:
            return

        self.has_finished = True
        self.failed.emit(message)
