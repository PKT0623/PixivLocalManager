class UpdateCheckWorkerSummaryMixin:
    def _update_summary(
        self,
        result_label: str,
        missing_count,
    ):
        self.summary["total"] += 1

        if result_label == "최신":
            self.summary["latest"] += 1
        elif result_label == "업데이트 필요":
            self.summary["need_update"] += 1
        elif result_label == "오류":
            self.summary["error"] += 1
        elif result_label == "스킵":
            self.summary["skipped"] += 1

        try:
            self.summary["missing"] += int(
                missing_count
            )
        except (TypeError, ValueError):
            pass

        self.summary_updated.emit(
            self.summary.copy()
        )

    def _status_label(
        self,
        result: dict,
    ) -> str:
        result_label = result.get(
            "result_label"
        )

        if result_label:
            return result_label

        status = result.get("status")

        if status == "need_update":
            return "업데이트 필요"

        if status == "up_to_date":
            return "최신"

        if status == "unknown":
            return "미확인"

        if status == "error":
            return "오류"

        return "확인 완료"
