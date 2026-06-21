from datetime import datetime
from pathlib import Path
import time


class ScanRunnerMixin:
    def _run_scan(self):
        started_at = datetime.now()
        start_timestamp = time.monotonic()

        try:
            self.runtime_info_updated.emit(
                self._build_runtime_info(
                    started_at=started_at,
                    start_timestamp=start_timestamp,
                    current=0,
                    total=0,
                )
            )

            artist_folders = self._get_artist_folders()
            validation_result = self._validate_artist_folders(artist_folders)

            for row_data in validation_result["log_rows"]:
                self.scan_result_requested.emit(row_data)

            artist_folders = validation_result["scannable_folders"]
            run_state = self._create_run_state(
                started_at=started_at,
                start_timestamp=start_timestamp,
                artist_folders=artist_folders,
            )

            self._restore_run_state_if_needed(run_state)

            self.target_count_changed.emit(run_state["total_count"])
            self.progress_updated.emit(
                run_state["completed_count"],
                run_state["total_count"],
            )

            if not artist_folders:
                self.log_message_requested.emit(
                    "스캔 가능한 작가 폴더가 없습니다."
                )
                finished_result = self._build_finished_result(
                    started_at=started_at,
                    start_timestamp=start_timestamp,
                    total=0,
                    summary=self._create_summary(),
                    statistics=self._create_statistics(),
                )
                self.finished.emit(finished_result)
                return

            self.log_message_requested.emit(
                f"스캔 대상 작가 폴더: {len(artist_folders)}개"
            )

            self.summary_updated.emit(run_state["summary"])
            self.statistics_updated.emit(run_state["statistics"])

            for local_index, folder_path in enumerate(
                artist_folders,
                start=1,
            ):
                self.current_folder_changed.emit(folder_path.name)

                try:
                    result = self._scan_artist_folder(folder_path)
                    action = result.get("action")
                    artist = result.get("artist") or {}
                    scan_result = result.get("scan_result")

                    result_label = self._result_label(action)
                    self._increase_summary(run_state["summary"], action)
                    self._increase_statistics(
                        run_state["statistics"],
                        scan_result,
                    )

                    self.scan_result_requested.emit(
                        self._build_scan_result_row(
                            index=run_state["completed_count"] + 1,
                            total=run_state["total_count"],
                            result=result_label,
                            artist=artist,
                            folder_path=folder_path,
                        )
                    )
                except Exception as error:
                    run_state["summary"]["failed"] += 1

                    self.scan_result_requested.emit(
                        self._build_failed_result_row(
                            index=run_state["completed_count"] + 1,
                            total=run_state["total_count"],
                            folder_path=folder_path,
                            error=error,
                        )
                    )

                self._increase_completed_count(run_state)
                self.summary_updated.emit(run_state["summary"])
                self.statistics_updated.emit(run_state["statistics"])
                self.progress_updated.emit(
                    run_state["completed_count"],
                    run_state["total_count"],
                )
                self.runtime_info_updated.emit(
                    self._build_runtime_info(
                        started_at=started_at,
                        start_timestamp=start_timestamp,
                        current=run_state["completed_count"],
                        total=run_state["total_count"],
                    )
                )

                if self._should_stop_after_item(
                    run_state,
                    artist_folders,
                    local_index,
                ):
                    return

                if self._should_pause_after_item(
                    run_state,
                    artist_folders,
                    local_index,
                ):
                    return

            self.current_folder_changed.emit("-")
            self.log_message_requested.emit(
                "전체 스캔 완료: "
                f"등록 {run_state['summary']['created']}개, "
                f"업데이트 {run_state['summary']['updated']}개, "
                f"변경 없음 {run_state['summary']['unchanged']}개, "
                f"실패 {run_state['summary']['failed']}개, "
                f"총 파일 {run_state['statistics']['total_file_count']}개, "
                f"총 작품 {run_state['statistics']['total_artwork_count']}개"
            )
        except Exception as error:
            self.failed.emit(str(error))
            return

        finished_result = self._build_finished_result(
            started_at=started_at,
            start_timestamp=start_timestamp,
            total=run_state["total_count"],
            summary=run_state["summary"],
            statistics=run_state["statistics"],
        )
        self.finished.emit(finished_result)

    def _scan_artist_folder(self, folder_path: Path) -> dict:
        return self.artist_service.save_scanned_artist(
            str(folder_path)
        )
