from ui.dialogs.update_check_dialog import UpdateCheckDialog

from .filters import (
    DEFAULT_SORT_REVERSE,
    STATUS_SORT_ORDERS,
    filter_artists,
    sort_artists,
)


class ArtistsActions:
    def __init__(self, page):
        self.page = page

    def load_artists(self):
        self.page.all_artists = self.page.artist_service.get_all_artists()
        self.apply_filter_and_sort()

    def apply_filter_and_sort(self):
        keyword = self.page.toolbar.search_input.text()
        artists = filter_artists(
            self.page.all_artists,
            keyword,
        )

        artists = sort_artists(
            artists,
            self.page.sort_field,
            self.page.sort_reverse,
            self.page.status_sort_index,
        )

        self.page.artist_table.set_artists(artists)

    def open_update_check_dialog(self):
        dialog = UpdateCheckDialog(
            self.page.all_artists,
            self.page,
        )
        dialog.update_finished.connect(self.load_artists)
        dialog.exec()

        self.load_artists()

    def handle_sort_requested(self, sort_field: str):
        if sort_field == "update_status":
            self.page.sort_field = sort_field
            self.page.status_sort_index = (
                self.page.status_sort_index + 1
            ) % len(STATUS_SORT_ORDERS)
            self.apply_filter_and_sort()
            return

        if self.page.sort_field == sort_field:
            self.page.sort_reverse = not self.page.sort_reverse
        else:
            self.page.sort_field = sort_field
            self.page.sort_reverse = DEFAULT_SORT_REVERSE.get(
                sort_field,
                False,
            )

        self.apply_filter_and_sort()

    def toggle_rating_display(self):
        if self.page.rating_display_mode == "stars":
            self.page.rating_display_mode = "number"
            self.page.toolbar.rating_toggle_button.setText("평점: 숫자")
        else:
            self.page.rating_display_mode = "stars"
            self.page.toolbar.rating_toggle_button.setText("평점: 별")

        self.page.artist_table.set_rating_display_mode(
            self.page.rating_display_mode
        )
