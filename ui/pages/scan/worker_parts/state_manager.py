from datetime import datetime
from pathlib import Path


class StateManagerMixin:
    def _create_run_state(
        self,
        started_at: datetime,
        start_timestamp: float,
        artist_folders: list[Path],
    ) -> dict:
        return {
            "started_at": started_at,
            "start_timestamp": start_timestamp,
            "root_folder_path": self.root_folder_path,
            "preview_mode": self.preview_mode,
            "total_count": len(artist_folders),
            "completed_count": 0,
            "summary": self._create_summary(),
            "statistics": self._create_statistics(),
        }

    def _restore_run_state_if_needed(
        self,
        run_state: dict,
    ):
        if not self.resume_payload:
            return

        run_state["total_count"] = int(
            self.resume_payload.get("total_count", 0)
            or run_state["total_count"]
        )
        run_state["completed_count"] = int(
            self.resume_payload.get("completed_count", 0) or 0
        )
        run_state["summary"] = dict(
            self.resume_payload.get("summary", {}) or self._create_summary()
        )
        run_state["statistics"] = dict(
            self.resume_payload.get("statistics", {})
            or self._create_statistics()
        )

    def _increase_completed_count(
        self,
        run_state: dict,
    ):
        run_state["completed_count"] = int(
            run_state.get("completed_count", 0) or 0
        ) + 1
