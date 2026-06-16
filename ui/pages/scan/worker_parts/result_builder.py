from datetime import datetime
from pathlib import Path
import time


class ResultBuilderMixin:
    def _result_label(self, action: str | None) -> str:
        if action == "created":
            return "등록"

        if action == "updated":
            return "업데이트"

        if action == "unchanged":
            return "변경 없음"

        return "업데이트"

    def _build_finished_result(
        self,
        started_at: datetime,
        start_timestamp: float,
        total: int,
        summary: dict,
        statistics: dict,
    ) -> dict:
        finished_at = datetime.now()
        duration_seconds = max(
            0,
            int(time.monotonic() - start_timestamp),
        )

        return {
            "started_at": started_at.isoformat(),
            "started_at_text": started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "finished_at": finished_at.isoformat(),
            "finished_at_text": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": duration_seconds,
            "duration_text": self._format_seconds(duration_seconds),
            "root_folder_path": self.root_folder_path,
            "total": total,
            "created": int(summary.get("created", 0) or 0),
            "updated": int(summary.get("updated", 0) or 0),
            "unchanged": int(summary.get("unchanged", 0) or 0),
            "failed": int(summary.get("failed", 0) or 0),
            "total_file_count": int(
                statistics.get("total_file_count", 0) or 0
            ),
            "total_artwork_count": int(
                statistics.get("total_artwork_count", 0) or 0
            ),
            "extension_counts": statistics.get("extension_counts", {}) or {},
        }

    def _build_scan_result_row(
        self,
        index: int,
        total: int,
        result: str,
        artist: dict,
        folder_path: Path,
    ) -> dict:
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": f"{index}/{total}",
            "result": result,
            "artist_id": artist.get("id"),
            "artist_name": str(artist.get("artist_name", "") or "-"),
            "pixiv_id": str(artist.get("pixiv_id", "") or "-"),
            "artwork_count": str(artist.get("folder_artwork_count", 0)),
            "file_count": str(artist.get("folder_file_count", 0)),
            "update_status": str(artist.get("update_status", "") or "-"),
            "folder_path": str(folder_path),
            "error_message": "-",
        }

    def _build_failed_result_row(
        self,
        index: int,
        total: int,
        folder_path: Path,
        error: Exception,
    ) -> dict:
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": f"{index}/{total}",
            "result": "실패",
            "artist_id": None,
            "artist_name": folder_path.name,
            "pixiv_id": "-",
            "artwork_count": "-",
            "file_count": "-",
            "update_status": "error",
            "folder_path": str(folder_path),
            "error_message": str(error),
        }

    def _build_validation_row(
        self,
        index: int,
        total: int,
        result: str,
        artist_name: str,
        pixiv_id: str,
        folder_path: Path,
        message: str,
    ) -> dict:
        progress = "-"

        if index > 0 and total > 0:
            progress = f"{index}/{total}"

        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": progress,
            "result": result,
            "artist_id": None,
            "artist_name": artist_name or folder_path.name,
            "pixiv_id": pixiv_id or "-",
            "artwork_count": "-",
            "file_count": "-",
            "update_status": "-",
            "folder_path": str(folder_path),
            "error_message": message,
        }
