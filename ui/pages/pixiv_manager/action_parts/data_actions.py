class PixivManagerDataActions:
    def load_saved_page_size(self):
        saved_page_size = self.settings_service.get_setting(
            self.PAGE_SIZE_SETTING_KEY
        )

        if not saved_page_size:
            return

        index = self.page.page_size_combo.findText(str(saved_page_size))

        if index < 0:
            return

        self.page.page_size_combo.blockSignals(True)
        self.page.page_size_combo.setCurrentIndex(index)
        self.page.page_size_combo.blockSignals(False)

    def handle_page_size_changed(self):
        page_size = self.page.page_size_combo.currentText()

        try:
            self.settings_service.set_setting(
                self.PAGE_SIZE_SETTING_KEY,
                page_size,
            )
        except Exception as error:
            self._log_message(f"페이지 크기 저장 실패: {error}")

        self.reset_page_and_apply_filters()

    def load_data(self):
        self.follow_users = self.follow_service.get_all_follow_users()
        self.bookmark_artworks = (
            self.bookmark_service.get_all_bookmark_artworks()
        )

        self.page.summary_section.update_summary(
            self._build_summary(
                follow_users=self.follow_users,
                bookmark_artworks=self.bookmark_artworks,
            )
        )

        self.apply_filters()

        self.page.status_label.setText(
            "Pixiv 관리 데이터를 새로고침했습니다."
        )

    def reset_page_and_apply_filters(self):
        self.current_page = 1
        self.apply_filters()

    def apply_filters(self):
        source_items, id_field = self._get_current_source_items()
        self.filtered_items = self._filter_items(
            items=source_items,
            id_field=id_field,
        )

        page_items = self._get_current_page_items(self.filtered_items)
        self._load_current_table(page_items)
        self._update_page_labels(
            total_count=len(source_items),
            filtered_count=len(self.filtered_items),
            page_count=len(page_items),
        )

    def handle_tab_changed(self):
        self.current_page = 1
        self.apply_filters()

    def _get_current_source_items(self) -> tuple[list[dict], str]:
        if self.page.tab_widget.currentIndex() == 0:
            return self.follow_users, "pixiv_user_id"

        return self.bookmark_artworks, "artwork_id"

    def _load_current_table(
        self,
        page_items: list[dict],
    ):
        if self.page.tab_widget.currentIndex() == 0:
            self.page.follow_table.load_follow_users(page_items)
            return

        self.page.bookmark_table.load_bookmark_artworks(page_items)

    def _filter_items(
        self,
        items: list[dict],
        id_field: str,
    ) -> list[dict]:
        category = self.page.filter_combo.currentText()

        filtered_items = []

        for item in items:
            if not self._match_category(item, category):
                continue

            filtered_items.append(item)

        return filtered_items

    def _match_category(
        self,
        item: dict,
        category: str,
    ) -> bool:
        if category == "전체":
            return True

        if category == "등록":
            return bool(item.get("is_local_artist"))

        sync_status = str(item.get("sync_status", "") or "pending")

        if category == "동기화 필요":
            return (
                not str(item.get("last_synced_at", "") or "").strip()
                or sync_status in {"pending", "failed"}
            )

        if category == "완료":
            return sync_status == "synced"

        if category == "대기":
            return sync_status == "pending"

        if category == "실패":
            return sync_status == "failed"

        if category == "스킵":
            return sync_status == "skipped"

        return True

    def _build_summary(
        self,
        follow_users: list[dict],
        bookmark_artworks: list[dict],
    ) -> dict:
        follow_total = len(follow_users)
        bookmark_total = len(bookmark_artworks)

        follow_matched = sum(
            1
            for item in follow_users
            if item.get("is_local_artist")
        )
        bookmark_matched = sum(
            1
            for item in bookmark_artworks
            if item.get("is_local_artist")
        )

        return {
            "follow_total": follow_total,
            "follow_matched": follow_matched,
            "follow_unmatched": follow_total - follow_matched,
            "bookmark_total": bookmark_total,
            "bookmark_matched": bookmark_matched,
            "bookmark_unmatched": bookmark_total - bookmark_matched,
        }

    def _log_message(
        self,
        message: str,
    ):
        if hasattr(self.page, "log_message"):
            self.page.log_message(message)
            return

        if hasattr(self.page, "status_label"):
            self.page.status_label.setText(message)
