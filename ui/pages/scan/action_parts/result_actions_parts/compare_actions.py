class ScanResultCompareActionsMixin:
    def _build_latest_compare_result(
        self,
        history: list[dict],
    ) -> dict | None:
        if len(history) < 2:
            return None

        latest = history[0]
        previous = history[1]

        return self._build_compare_result(
            latest=latest,
            previous=previous,
        )

    def _build_compare_result(
        self,
        latest: dict,
        previous: dict,
    ) -> dict:
        fields = [
            ("total", "대상"),
            ("created", "등록"),
            ("updated", "업데이트"),
            ("unchanged", "변경 없음"),
            ("failed", "실패"),
            ("total_file_count", "파일"),
            ("total_artwork_count", "작품"),
            ("non_artwork_file_count", "비작품"),
        ]

        items = []

        for key, label in fields:
            latest_value = self._safe_int(latest.get(key))
            previous_value = self._safe_int(previous.get(key))
            diff = latest_value - previous_value

            items.append(
                {
                    "key": key,
                    "label": label,
                    "latest": latest_value,
                    "previous": previous_value,
                    "diff": diff,
                }
            )

        return {
            "latest_finished_at": latest.get("finished_at_text", "-"),
            "previous_finished_at": previous.get("finished_at_text", "-"),
            "items": items,
        }

    def _safe_int(
        self,
        value,
    ) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0
