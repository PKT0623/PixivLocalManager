from datetime import datetime
import time


class PreviewRunnerMixin:
    def _run_preview(self):
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

            preview_rows = []

            for row_data in validation_result["log_rows"]:
                if row_data.get("result") == "오류":
                    preview_rows.append(
                        self._build_preview_error_row(row_data)
                    )

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

            if not artist_folders and not preview_rows:
                self.log_message_requested.emit(
                    "미리보기 가능한 작가 폴더가 없습니다."
                )
                self.preview_result_requested.emit([])
                self.preview_summary_updated.emit(self._create_summary())
                self.finished.emit(
                    self._build_finished_result(
                        started_at=started_at,
                        start_timestamp=start_timestamp,
                        total=0,
                        summary=self._create_summary(),
                        statistics=self._create_statistics(),
                    )
                )
                return

            if not self.resume_payload:
                self.log_message_requested.emit(
                    f"스캔 미리보기 시작: {len(artist_folders)}개"
                )

            existing_artists = self.artist_service.get_all_artists()
            existing_by_pixiv_id = self._build_existing_pixiv_id_map(
                existing_artists
            )

            for local_index, folder_path in enumerate(
                artist_folders,
                start=1,
            ):
                self.current_folder_changed.emit(folder_path.name)

                try:
                    row = self._preview_artist_folder(
                        folder_path=folder_path,
                        existing_by_pixiv_id=existing_by_pixiv_id,
                    )
                    preview_rows.append(row)
                    self._increase_preview_summary(run_state["summary"], row)
                    self._increase_statistics(
                        run_state["statistics"],
                        row.get("scan_result"),
                    )
                except Exception as error:
                    error_row = self._build_preview_exception_row(
                        folder_path,
                        error,
                    )
                    preview_rows.append(error_row)
                    self._increase_preview_summary(
                        run_state["summary"],
                        error_row,
                    )

                self._increase_completed_count(run_state)
                self.preview_summary_updated.emit(run_state["summary"])
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

                if self._should_stop_after_preview_item(
                    run_state,
                    artist_folders,
                    local_index,
                    preview_rows,
                ):
                    return

                if self._should_pause_after_preview_item(
                    run_state,
                    artist_folders,
                    local_index,
                    preview_rows,
                ):
                    return

            self.current_folder_changed.emit("-")
            self.preview_result_requested.emit(
                self._strip_preview_runtime_objects(preview_rows)
            )
            self.preview_summary_updated.emit(run_state["summary"])
            self.log_message_requested.emit(
                "스캔 미리보기 완료: "
                f"신규 {run_state['summary']['created']}개, "
                f"업데이트 {run_state['summary']['updated']}개, "
                f"변경 없음 {run_state['summary']['unchanged']}개, "
                f"오류 예상 {run_state['summary']['failed']}개"
            )
        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit(
            self._build_finished_result(
                started_at=started_at,
                start_timestamp=start_timestamp,
                total=run_state["total_count"],
                summary=run_state["summary"],
                statistics=run_state["statistics"],
            )
        )
