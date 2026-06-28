from ..utils import folder_status_label

from .artwork_actions_parts import (
    ArtworkClipboardActionsMixin,
    ArtworkMissingTableMixin,
    ArtworkOpenActionsMixin,
    ArtworkRecentTableMixin,
    ArtworkWidgetFactoryMixin,
)


class ArtistArtworkActions(
    ArtworkClipboardActionsMixin,
    ArtworkOpenActionsMixin,
    ArtworkMissingTableMixin,
    ArtworkRecentTableMixin,
    ArtworkWidgetFactoryMixin,
):
    PIXIV_ARTIST_URL = "https://www.pixiv.net/users/{pixiv_id}"
    PIXIV_ARTWORK_URL = "https://www.pixiv.net/artworks/{artwork_id}"

    def select_folder(self):
        current_path = self.page.info_section.folder_path_input.text().strip()

        if current_path == "-":
            current_path = ""

        folder_path = self.get_existing_directory(
            self.page,
            "작가 폴더 선택",
            current_path,
        )

        if not folder_path:
            return

        self.page.info_section.folder_path_input.setText(folder_path)
        self.page.info_section.folder_status_label.setText(
            folder_status_label(folder_path)
        )

        self.set_recent_local_artwork_table_data(folder_path)
