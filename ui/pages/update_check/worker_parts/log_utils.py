from datetime import datetime


class UpdateCheckWorkerLogMixin:
    def _should_skip_recent(
        self,
        artist: dict,
    ) -> bool:
        if not self.skip_recent:
            return False

        return (
            self.artist_service
            .update_service
            .update_utils
            .was_recently_checked(artist)
        )

    def _handle_artist_result(
        self,
        result: dict,
        previous_history: dict | None,
        index: int,
        total: int,
    ):
        artist = result.get("artist") or {}

        result_label = self._status_label(
            result
        )

        missing_count = result.get(
            "missing_count",
            0,
        )

        comparison = (
            self.history_repo.build_comparison(
                current_history={
                    "missing_count": missing_count,
                    "missing_ids": self._ids_to_text(
                        result.get("missing_ids")
                    ),
                },
                previous_history=previous_history,
            )
        )

        self._update_summary(
            result_label,
            missing_count,
        )

        self.log_requested.emit(
            {
                "time": datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "progress": f"{index}/{total}",
                "result": result_label,
                "artist_name": artist.get(
                    "artist_name",
                    "-",
                ),
                "pixiv_id": artist.get(
                    "pixiv_id",
                    "-",
                ),
                "local_count": result.get(
                    "local_count",
                    "-",
                ),
                "pixiv_count": result.get(
                    "pixiv_count",
                    "-",
                ),
                "missing_count": missing_count,
                "missing_delta": comparison.get(
                    "missing_delta",
                    0,
                ),
                "has_previous": comparison.get(
                    "has_previous",
                    False,
                ),
                "new_missing_count": comparison.get(
                    "new_missing_count",
                    0,
                ),
                "resolved_missing_count": comparison.get(
                    "resolved_missing_count",
                    0,
                ),
                "missing_ids": self._ids_to_text(
                    result.get("missing_ids")
                ),
                "new_missing_ids": comparison.get(
                    "new_missing_ids",
                    "",
                ),
                "resolved_missing_ids": comparison.get(
                    "resolved_missing_ids",
                    "",
                ),
                "download_candidate_ids": (
                    self._ids_to_text(
                        result.get(
                            "download_candidate_ids"
                        )
                    )
                ),
                "status": result.get(
                    "status",
                    "-",
                ),
            }
        )

    def _handle_skipped_recent(
        self,
        artist: dict,
        index: int,
        total: int,
    ):
        self.artist_service.update_service.save_skipped_recent_history(
            artist
        )

        self._update_summary(
            "스킵",
            0,
        )

        self.log_requested.emit(
            {
                "time": datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "progress": f"{index}/{total}",
                "result": "스킵",
                "artist_name": artist.get(
                    "artist_name",
                    "-",
                ),
                "pixiv_id": artist.get(
                    "pixiv_id",
                    "-",
                ),
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": 0,
                "missing_delta": "-",
                "has_previous": False,
                "new_missing_count": "-",
                "resolved_missing_count": "-",
                "missing_ids": "",
                "new_missing_ids": "",
                "resolved_missing_ids": "",
                "download_candidate_ids": "",
                "status": (
                    "최근 1일 이내 확인한 작가"
                ),
            }
        )

    def _handle_error(
        self,
        artist_id: int,
        index: int,
        total: int,
        message: str,
    ):
        self.failed_artist_detected.emit(
            artist_id
        )

        self._update_summary(
            "오류",
            0,
        )

        self.log_requested.emit(
            {
                "time": datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "progress": f"{index}/{total}",
                "result": "오류",
                "artist_name": (
                    f"artist_id={artist_id}"
                ),
                "pixiv_id": "-",
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": "-",
                "missing_delta": "-",
                "has_previous": False,
                "new_missing_count": "-",
                "resolved_missing_count": "-",
                "missing_ids": "",
                "new_missing_ids": "",
                "resolved_missing_ids": "",
                "download_candidate_ids": "",
                "status": message,
            }
        )

    def _emit_info(
        self,
        current: int,
        total: int,
        result: str,
        message: str,
    ):
        self.log_requested.emit(
            {
                "time": datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "progress": f"{current}/{total}",
                "result": result,
                "artist_name": message,
                "pixiv_id": "-",
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": "-",
                "missing_delta": "-",
                "has_previous": False,
                "new_missing_count": "-",
                "resolved_missing_count": "-",
                "missing_ids": "",
                "new_missing_ids": "",
                "resolved_missing_ids": "",
                "download_candidate_ids": "",
                "status": "-",
            }
        )

    def _ids_to_text(
        self,
        values,
    ) -> str:
        if not values:
            return ""

        if isinstance(values, str):
            return values

        return ",".join(
            str(value).strip()
            for value in values
            if str(value).strip()
        )
