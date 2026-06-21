class PixivManagerDeleteActions:
    def delete_selected(self):
        if self._is_worker_running():
            return

        if self.page.tab_widget.currentIndex() == 0:
            ids = self.page.follow_table.get_checked_ids()
            self._delete_follow_users(ids, "선택 삭제")
            return

        ids = self.page.bookmark_table.get_checked_ids()
        self._delete_bookmark_artworks(ids, "선택 삭제")

    def delete_displayed(self):
        if self._is_worker_running():
            return

        if self.page.tab_widget.currentIndex() == 0:
            ids = self.page.follow_table.get_displayed_ids()
            self._delete_follow_users(ids, "현재 페이지 삭제")
            return

        ids = self.page.bookmark_table.get_displayed_ids()
        self._delete_bookmark_artworks(ids, "현재 페이지 삭제")

    def _delete_follow_users(
        self,
        ids: list[int],
        action_label: str,
    ):
        if not ids:
            self.page.status_label.setText("삭제할 팔로우 유저가 없습니다.")
            return

        deleted_count = 0
        error_count = 0

        for follow_user_id in ids:
            try:
                self.follow_service.delete_follow_user(follow_user_id)
                deleted_count += 1
            except Exception:
                error_count += 1

        self._add_log(
            target="팔로우",
            result="완료",
            message=f"{action_label}: {deleted_count}명 삭제",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=error_count,
        )

        self.load_data()
        self.page.status_label.setText(
            f"팔로우 유저 {deleted_count}명을 삭제했습니다."
        )

    def _delete_bookmark_artworks(
        self,
        ids: list[int],
        action_label: str,
    ):
        if not ids:
            self.page.status_label.setText("삭제할 북마크 작품이 없습니다.")
            return

        deleted_count = 0
        error_count = 0

        for bookmark_artwork_id in ids:
            try:
                self.bookmark_service.delete_bookmark_artwork(
                    bookmark_artwork_id
                )
                deleted_count += 1
            except Exception:
                error_count += 1

        self._add_log(
            target="북마크",
            result="완료",
            message=f"{action_label}: {deleted_count}개 삭제",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=error_count,
        )

        self.load_data()
        self.page.status_label.setText(
            f"북마크 작품 {deleted_count}개를 삭제했습니다."
        )
