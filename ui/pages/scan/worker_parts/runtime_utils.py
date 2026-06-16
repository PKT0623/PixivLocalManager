import time


class RuntimeUtilsMixin:
    def _build_runtime_info(
        self,
        started_at,
        start_timestamp: float,
        current: int,
        total: int,
    ) -> dict:
        elapsed_seconds = max(
            0,
            int(time.monotonic() - start_timestamp),
        )
        speed = 0.0

        if elapsed_seconds > 0 and current > 0:
            speed = current / elapsed_seconds

        remaining_seconds = None

        if speed > 0 and total > current:
            remaining_seconds = int((total - current) / speed)

        return {
            "start_time_text": started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_time_text": self._format_seconds(elapsed_seconds),
            "speed_text": self._format_speed(speed),
            "estimated_time_text": self._format_remaining_time(
                remaining_seconds
            ),
        }

    def _format_seconds(
        self,
        seconds: int,
    ) -> str:
        seconds = max(0, int(seconds or 0))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remain_seconds = seconds % 60

        if hours > 0:
            return f"{hours}시간 {minutes}분 {remain_seconds}초"

        if minutes > 0:
            return f"{minutes}분 {remain_seconds}초"

        return f"{remain_seconds}초"

    def _format_speed(
        self,
        speed: float,
    ) -> str:
        if speed <= 0:
            return "-"

        return f"{speed:.2f}개/초"

    def _format_remaining_time(
        self,
        seconds: int | None,
    ) -> str:
        if seconds is None:
            return "-"

        return self._format_seconds(seconds)
