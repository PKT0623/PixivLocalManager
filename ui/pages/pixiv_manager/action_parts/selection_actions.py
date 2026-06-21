class PixivManagerSelectionActions:
    def select_all_displayed(self):
        if self.page.tab_widget.currentIndex() == 0:
            self.page.follow_table.check_all()
            return

        self.page.bookmark_table.check_all()

    def clear_selection(self):
        if self.page.tab_widget.currentIndex() == 0:
            self.page.follow_table.clear_checks()
            return

        self.page.bookmark_table.clear_checks()

    def open_selected_pixiv(self):
        if self.page.tab_widget.currentIndex() == 0:
            self.page.follow_table.open_selected_pixiv()
            return

        self.page.bookmark_table.open_selected_pixiv()
