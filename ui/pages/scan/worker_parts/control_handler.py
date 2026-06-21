from pathlib import Path


class ControlHandlerMixin:
    def _should_stop_after_item(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
    ) -> bool:
        if not self.stop_requested:
            return False

        self.current_folder_changed.emit("-")
        self.stopped.emit(
            self._build_control_payload(
                run_state,
                artist_folders,
                local_index,
            )
        )
        return True

    def _should_pause_after_item(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
    ) -> bool:
        if not self.pause_requested:
            return False

        self.current_folder_changed.emit("-")
        self.paused.emit(
            self._build_control_payload(
                run_state,
                artist_folders,
                local_index,
            )
        )
        return True

    def _should_stop_after_preview_item(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
        preview_rows: list[dict],
    ) -> bool:
        if not self.stop_requested:
            return False

        self.current_folder_changed.emit("-")
        self.preview_result_requested.emit(
            self._strip_preview_runtime_objects(preview_rows)
        )
        self.stopped.emit(
            self._build_control_payload(
                run_state,
                artist_folders,
                local_index,
            )
        )
        return True

    def _should_pause_after_preview_item(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
        preview_rows: list[dict],
    ) -> bool:
        if not self.pause_requested:
            return False

        self.current_folder_changed.emit("-")
        self.preview_result_requested.emit(
            self._strip_preview_runtime_objects(preview_rows)
        )
        self.paused.emit(
            self._build_control_payload(
                run_state,
                artist_folders,
                local_index,
            )
        )
        return True

    def _build_control_payload(
        self,
        run_state: dict,
        artist_folders: list[Path],
        local_index: int,
    ) -> dict:
        remaining_folders = artist_folders[local_index:]

        return {
            "root_folder_path": self.root_folder_path,
            "preview_mode": self.preview_mode,
            "total_count": int(run_state.get("total_count", 0) or 0),
            "completed_count": int(run_state.get("completed_count", 0) or 0),
            "summary": dict(run_state.get("summary", {}) or {}),
            "statistics": dict(run_state.get("statistics", {}) or {}),
            "remaining_folder_paths": [
                str(folder_path)
                for folder_path in remaining_folders
            ],
        }

    def _get_artist_folders(self) -> list[Path]:
        if self.target_folder_paths is not None:
            return [
                Path(folder_path)
                for folder_path in self.target_folder_paths
                if str(folder_path or "").strip()
            ]

        root_folder = Path(self.root_folder_path)

        if not root_folder.exists() or not root_folder.is_dir():
            raise ValueError("선택한 폴더가 존재하지 않습니다.")

        return self.folder_scanner.find_artist_folders(
            root_folder,
            max_depth=3,
        )
