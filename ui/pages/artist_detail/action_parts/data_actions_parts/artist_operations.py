from ...utils import status_label, to_int


class ArtistOperationsActions:
    def rescan_artist(self):
        if self.page.artist_id is None:
            self.show_warning(
                "재스캔 오류",
                "재스캔할 작가 정보가 없습니다.",
            )
            return

        try:
            self.page.artist_service.rescan_artist_folder(
                self.page.artist_id,
            )
        except Exception as error:
            self.show_warning(
                "재스캔 오류",
                f"현재 작가를 재스캔하지 못했습니다.\n{error}",
            )
            return

        self.refresh_artist()
        self.page.artist_updated.emit(self.page.artist_id)

        self.show_status_message("현재 작가 폴더를 다시 스캔했습니다.")

    def check_artist_update(self):
        if self.page.artist_id is None:
            self.show_warning(
                "업데이트 확인 오류",
                "업데이트를 확인할 작가 정보가 없습니다.",
            )
            return

        try:
            result = self.page.artist_service.check_artist_update(
                self.page.artist_id,
            )
        except Exception as error:
            self.show_warning(
                "업데이트 확인 오류",
                f"현재 작가의 업데이트를 확인하지 못했습니다.\n{error}",
            )
            return

        self.refresh_artist()
        self.page.artist_updated.emit(self.page.artist_id)

        missing_count = to_int(
            result.get("missing_count", 0),
            minimum=0,
        )
        status_text = status_label(result.get("status"))

        self.show_status_message(
            f"업데이트 상태: {status_text} / 누락 작품 수: {missing_count}"
        )
