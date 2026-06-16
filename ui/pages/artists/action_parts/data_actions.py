from ui.dialogs.update_check import UpdateCheckDialog

from ..filters import (
    DEFAULT_SORT_REVERSE,
    filter_artists,
    sort_artists,
)


MAX_SORT_RULES = 3


class ArtistsDataActions:
    def load_artists(self):
        self.page.all_artists = self.page.artist_service.get_all_artists()
        self.apply_filter_and_sort()

    def reload_artists_keep_selection(
        self,
        artist_ids: list[int],
    ):
        self.load_artists()
        self.page.artist_table.select_artist_ids(artist_ids)
        self.page.artist_table.setFocus()

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
            self.page.sort_rules,
        )

        self.page.artist_table.set_artists(artists)
        self.page.artist_table.set_sort_indicators(
            self.page.sort_rules,
        )

    def reset_filters(self):
        self.page.toolbar.reset_filter_values()
        self.apply_filter_and_sort()

    def reset_sort(self):
        self.page.sort_rules = self.page.default_sort_rules.copy()
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

    def handle_sort_requested(
        self,
        sort_field: str,
        is_multi_sort: bool,
    ):
        if is_multi_sort:
            self._handle_multi_sort_requested(sort_field)
        else:
            self._handle_single_sort_requested(sort_field)

        self.apply_filter_and_sort()

    def _handle_single_sort_requested(self, sort_field: str):
        current_rule = self._find_sort_rule(sort_field)

        if current_rule is None or len(self.page.sort_rules) > 1:
            sort_reverse = DEFAULT_SORT_REVERSE.get(
                sort_field,
                False,
            )
        else:
            sort_reverse = not current_rule[1]

        self.page.sort_rules = [
            (
                sort_field,
                sort_reverse,
            )
        ]

    def _handle_multi_sort_requested(self, sort_field: str):
        sort_rules = self.page.sort_rules.copy()

        for index, rule in enumerate(sort_rules):
            if rule[0] != sort_field:
                continue

            sort_rules[index] = (
                sort_field,
                not rule[1],
            )
            self.page.sort_rules = sort_rules
            return

        sort_rules.append(
            (
                sort_field,
                DEFAULT_SORT_REVERSE.get(
                    sort_field,
                    False,
                ),
            )
        )

        if len(sort_rules) > MAX_SORT_RULES:
            sort_rules = sort_rules[-MAX_SORT_RULES:]

        self.page.sort_rules = sort_rules

    def _find_sort_rule(
        self,
        sort_field: str,
    ) -> tuple[str, bool] | None:
        for rule in self.page.sort_rules:
            if rule[0] == sort_field:
                return rule

        return None

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

    def handle_rating_changed(
        self,
        artist_id: int,
        rating: int,
    ):
        try:
            self.page.artist_service.update_rating(
                artist_id,
                rating,
            )
        except Exception as error:
            print(error)
            return

        self.reload_artists_keep_selection([artist_id])
