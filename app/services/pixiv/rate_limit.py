import time


class PixivRateLimitService:
    DEFAULT_REQUEST_INTERVAL_MS = 2000
    DEFAULT_BATCH_SIZE = 1000
    DEFAULT_BATCH_REST_MS = 300000

    def __init__(
        self,
        request_interval_ms: int = DEFAULT_REQUEST_INTERVAL_MS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        batch_rest_ms: int = DEFAULT_BATCH_REST_MS,
        log_callback=None,
        status_callback=None,
    ):
        self.request_interval_ms = max(
            2000,
            int(request_interval_ms),
        )
        self.batch_size = max(
            1,
            int(batch_size),
        )
        self.batch_rest_ms = max(
            0,
            int(batch_rest_ms),
        )

        self.log_callback = log_callback
        self.status_callback = status_callback

        self.request_count = 0
        self.last_request_time = 0.0

    def set_callbacks(
        self,
        log_callback=None,
        status_callback=None,
    ):
        self.log_callback = log_callback
        self.status_callback = status_callback

    def wait_before_request(self):
        if self._should_rest_before_next_request():
            self.rest_batch()

        self._wait_request_interval()

        self.request_count += 1
        self.last_request_time = time.time()

    def rest_batch(self):
        if self.batch_rest_ms <= 0:
            return

        total_seconds = int(self.batch_rest_ms / 1000)

        self._emit_log(
            "휴식",
            (
                f"요청 {self.request_count}회 처리 완료. "
                f"{self._format_seconds(total_seconds)} 동안 휴식합니다."
            ),
        )

        self._safe_sleep(total_seconds)

        self._emit_log(
            "재개",
            "배치 휴식이 끝났습니다. Pixiv 요청을 재개합니다.",
        )

    def _should_rest_before_next_request(self) -> bool:
        if self.request_count <= 0:
            return False

        return self.request_count % self.batch_size == 0

    def _wait_request_interval(self):
        if self.last_request_time <= 0:
            return

        elapsed_ms = int((time.time() - self.last_request_time) * 1000)
        remain_ms = self.request_interval_ms - elapsed_ms

        if remain_ms <= 0:
            return

        self._safe_sleep(remain_ms / 1000)

    def _safe_sleep(
        self,
        seconds: float,
    ):
        end_time = time.time() + seconds

        while time.time() < end_time:
            remain_seconds = max(0, int(end_time - time.time()))

            self._emit_status(
                f"Pixiv 요청 대기 중: {self._format_seconds(remain_seconds)} 남음"
            )

            time.sleep(
                min(1.0, max(0.1, end_time - time.time()))
            )

    def _emit_log(
        self,
        result: str,
        message: str,
    ):
        if self.log_callback is None:
            return

        self.log_callback(
            result,
            message,
        )

    def _emit_status(
        self,
        message: str,
    ):
        if self.status_callback is None:
            return

        self.status_callback(message)

    def _format_seconds(
        self,
        seconds: int,
    ) -> str:
        if seconds <= 0:
            return "곧 완료"

        minutes = seconds // 60
        remain_seconds = seconds % 60

        if minutes <= 0:
            return f"{remain_seconds}초"

        return f"{minutes}분 {remain_seconds}초"
