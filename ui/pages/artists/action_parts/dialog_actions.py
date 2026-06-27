class ArtistsDialogActions:
    def show_information(self, title: str, message: str):
        self._show_status_message(title, message)

    def show_warning(self, title: str, message: str):
        self._show_status_message(title, message)

    def _show_status_message(self, title: str, message: str):
        title = str(title or "").strip()
        message = " ".join(
            str(message or "").split()
        )

        if title and message:
            self.page.show_status_message(f"{title}: {message}")
            return

        self.page.show_status_message(title or message)
