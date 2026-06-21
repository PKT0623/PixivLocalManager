class StatisticsMixin:
    def _create_summary(self) -> dict:
        return {
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "failed": 0,
        }

    def _create_statistics(self) -> dict:
        return {
            "total_file_count": 0,
            "total_artwork_count": 0,
            "extension_counts": {},
            "non_artwork_file_count": 0,
            "unsupported_extension_count": 0,
            "artwork_id_not_found_count": 0,
            "empty_file_count": 0,
            "scan_error_count": 0,
        }

    def _increase_preview_summary(
        self,
        summary: dict,
        row: dict,
    ):
        preview_result = str(row.get("preview_result", "") or "")

        if preview_result == "신규 등록 예정":
            summary["created"] += 1
            return

        if preview_result == "업데이트 예정":
            summary["updated"] += 1
            return

        if preview_result == "변경 없음 예정":
            summary["unchanged"] += 1
            return

        if preview_result == "오류 예상":
            summary["failed"] += 1

    def _increase_summary(
        self,
        summary: dict,
        action: str | None,
    ):
        if action == "created":
            summary["created"] += 1
            return

        if action == "updated":
            summary["updated"] += 1
            return

        if action == "unchanged":
            summary["unchanged"] += 1
            return

        summary["updated"] += 1

    def _increase_statistics(
        self,
        statistics: dict,
        scan_result,
    ):
        if scan_result is None:
            return

        statistics["total_file_count"] += int(
            getattr(scan_result, "folder_file_count", 0) or 0
        )
        statistics["total_artwork_count"] += int(
            getattr(scan_result, "folder_artwork_count", 0) or 0
        )

        extension_counts = getattr(scan_result, "extension_counts", {}) or {}

        for extension, count in extension_counts.items():
            statistics["extension_counts"][extension] = (
                statistics["extension_counts"].get(extension, 0)
                + int(count or 0)
            )

        non_artwork_summary = getattr(
            scan_result,
            "non_artwork_summary",
            {},
        ) or {}

        statistics["non_artwork_file_count"] += int(
            non_artwork_summary.get("total", 0) or 0
        )
        statistics["unsupported_extension_count"] += int(
            non_artwork_summary.get("unsupported_extension", 0) or 0
        )
        statistics["artwork_id_not_found_count"] += int(
            non_artwork_summary.get("artwork_id_not_found", 0) or 0
        )
        statistics["empty_file_count"] += int(
            non_artwork_summary.get("empty_file", 0) or 0
        )
        statistics["scan_error_count"] += int(
            non_artwork_summary.get("scan_error", 0) or 0
        )
