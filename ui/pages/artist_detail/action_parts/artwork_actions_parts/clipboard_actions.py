from PySide6.QtWidgets import QApplication


class ArtworkClipboardActionsMixin:
    def copy_folder_path(self):
        artist = self.page.current_artist

        if artist is None:
            return

        folder_path = str(artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        QApplication.clipboard().setText(folder_path)
        self.show_status_message("폴더 경로가 복사되었습니다.")

    def copy_pixiv_id(self):
        artist = self.page.current_artist

        if artist is None:
            return

        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        QApplication.clipboard().setText(pixiv_id)
        self.show_status_message("Pixiv ID가 복사되었습니다.")
