import time


class UpdateCheckWorkerSleepMixin:
    def _rest_between_requests(self):
        if self.request_interval_ms <= 0:
            return

        self._safe_sleep(
            self.request_interval_ms / 1000
        )

    def _rest_between_batches(
        self,
        current: int,
        total: int,
    ):
        if self.batch_rest_ms <= 0:
            return

        self._emit_info(
            current,
            total,
            "휴식",
            (
                f"{self.batch_size}명 처리 완료. "
                "잠시 대기합니다."
            ),
        )

        self._safe_sleep(
            self.batch_rest_ms / 1000
        )

    def _safe_sleep(
        self,
        seconds: float,
    ):
        end_time = time.time() + seconds

        while time.time() < end_time:
            if self.cancel_event.is_set():
                return

            if self.pause_event.is_set():
                return

            time.sleep(0.2)
