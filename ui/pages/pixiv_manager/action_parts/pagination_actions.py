from math import ceil


class PixivManagerPaginationActions:
    def prev_page(self):
        if self.current_page <= 1:
            return

        self.current_page -= 1
        self.apply_filters()

    def next_page(self):
        max_page = self._get_max_page(len(self.filtered_items))

        if self.current_page >= max_page:
            return

        self.current_page += 1
        self.apply_filters()

    def _get_page_size(self) -> int:
        try:
            return int(self.page.page_size_combo.currentText())
        except ValueError:
            return 100

    def _get_max_page(
        self,
        item_count: int,
    ) -> int:
        if item_count <= 0:
            return 1

        return max(1, ceil(item_count / self._get_page_size()))

    def _get_current_page_items(
        self,
        items: list[dict],
    ) -> list[dict]:
        max_page = self._get_max_page(len(items))

        if self.current_page > max_page:
            self.current_page = max_page

        if self.current_page < 1:
            self.current_page = 1

        page_size = self._get_page_size()
        start_index = (self.current_page - 1) * page_size
        end_index = start_index + page_size

        return items[start_index:end_index]

    def _update_page_labels(
        self,
        total_count: int,
        filtered_count: int,
        page_count: int,
    ):
        max_page = self._get_max_page(filtered_count)

        self.page.page_info_label.setText(
            f"페이지: {self.current_page} / {max_page}"
        )
        self.page.display_count_label.setText(
            f"표시: {page_count} / {filtered_count} "
            f"(전체 {total_count})"
        )

        self.page.prev_page_button.setEnabled(self.current_page > 1)
        self.page.next_page_button.setEnabled(self.current_page < max_page)
