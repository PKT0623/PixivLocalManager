from ui.dialogs.update_check import UpdateCheckDialog

from .filters import (
    DEFAULT_SORT_REVERSE,
    filter_artists,
    sort_artists,
)


class ArtistsActions:
    def __init__(self, page):
        self.page = page

    def load_artists(self):
        self.page.all_artists = self.page.artist_service.get_all_artists()
        self.apply_filter_and_sort()

    def apply_filter_and_sort(self, *args):
        toolbar = self.page.toolbar

        artists = filter_artists(
            self.page.all_artists,
            keyword=toolbar.search_input.text(),
            rating_value=toolbar.get_rating_filter_value(),
            rating_filter_mode=toolbar.get_rating_filter_mode(),
            favorite_only=toolbar.favorite_only_checkbox.isChecked(),
            update_required_only=(
                toolbar.update_required_only_checkbox.isChecked()
            ),
            unknown_only=toolbar.unknown_only_checkbox.isChecked(),
            unrated_only=toolbar.unrated_only_checkbox.isChecked(),
            exclude_hidden=toolbar.exclude_hidden_checkbox.isChecked(),
        )

        artists = sort_artists(
            artists,
            self.page.sort_field,
            self.page.sort_reverse,
        )

        self.page.artist_table.set_artists(artists)

    def reset_filters(self):
        self.page.toolbar.reset_filter_values()
        self.apply_filter_and_sort()

    def toggle_rating_filter_mode(self):
        self.page.toolbar.toggle_rating_filter_mode()
        self.apply_filter_and_sort()

    def open_update_check_dialog(self):
        dialog = UpdateCheckDialog(
            self.page.all_artists,
            self.page,
        )
        dialog.update_finished.connect(self.load_artists)
        dialog.exec()

        self.load_artists()

    def handle_sort_requested(self, sort_field: str):
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

    def handle_favorite_toggled(
        self,
        artist_id: int,
    ):
        try:
            self.page.artist_service.toggle_favorite(
                artist_id
            )
        except Exception as error:
            print(error)
            return

        self.load_artists()
