from PySide6.QtCore import Slot

from app.services.artist import ArtistService
from app.services.pixiv_update_service import PixivRequestError


class UpdateCheckWorkerRunMixin:
    @Slot()
    def run(self):
        self.artist_service = ArtistService()

        try:
            for offset, artist_id in enumerate(
                self.artist_ids,
                start=1,
            ):
                current = self.progress_offset + offset

                if self._should_cancel(current - 1):
                    return

                if self._should_pause(current - 1):
                    return

                self._check_artist(
                    artist_id,
                    current,
                    self.total_count,
                )

                self.progress_updated.emit(
                    current,
                    self.total_count,
                )

                if self._should_cancel(current):
                    return

                if self._should_pause(current):
                    return

                if offset < len(self.artist_ids):
                    self._rest_between_requests()

                if self._should_cancel(current):
                    return

                if self._should_pause(current):
                    return

                if (
                    offset % self.batch_size == 0
                    and current < self.total_count
                ):
                    self._rest_between_batches(
                        current,
                        self.total_count,
                    )

                    if self._should_cancel(current):
                        return

                    if self._should_pause(current):
                        return

        except Exception as error:
            self._emit_failed(str(error))
            return

        self._emit_finished()

    def _check_artist(
        self,
        artist_id: int,
        index: int,
        total: int,
    ):
        try:
            artist = self.artist_service.get_artist(artist_id)

            if artist is None:
                raise ValueError(
                    "작가를 찾을 수 없습니다."
                )

            if self._should_skip_recent(artist):
                self._handle_skipped_recent(
                    artist,
                    index,
                    total,
                )
                return

            previous_history = (
                self.history_repo.get_previous_by_artist_id(
                    artist_id
                )
            )

            result = self.artist_service.check_artist_update(
                artist_id
            )

            self._handle_artist_result(
                result=result,
                previous_history=previous_history,
                index=index,
                total=total,
            )

        except PixivRequestError as error:
            self._handle_error(
                artist_id,
                index,
                total,
                error.to_display_text(),
            )

            if error.should_stop:
                self.cancel_event.set()
                self._emit_failed(
                    error.to_display_text()
                )

        except Exception as error:
            self._handle_error(
                artist_id,
                index,
                total,
                f"[알 수 없는 오류] {error}",
            )
