from PySide6.QtCore import Qt

from ...utils import find_recent_local_artworks


class ArtworkRecentTableMixin:
    def set_recent_local_artwork_table_data(self, folder_path: str):
        section = self.page.info_section
        table = section.recent_local_artwork_table
        table.setRowCount(0)

        artworks = find_recent_local_artworks(
            folder_path,
            limit=10,
        )

        for artwork in artworks:
            row = table.rowCount()
            table.insertRow(row)

            artwork_id = artwork["artwork_id"]
            file_path = artwork["file_path"]

            table.setItem(
                row,
                0,
                self.create_readonly_item(
                    artwork_id,
                    Qt.AlignLeft | Qt.AlignVCenter,
                ),
            )
            table.setItem(
                row,
                1,
                self.create_readonly_item(str(artwork["file_count"])),
            )
            table.setItem(
                row,
                2,
                self.create_readonly_item(artwork["latest_modified_at"]),
            )

            pixiv_button = self.create_small_button("Pixiv")
            pixiv_button.clicked.connect(
                lambda checked=False, aid=artwork_id: (
                    self.open_pixiv_artwork(aid)
                )
            )

            folder_button = self.create_small_button("폴더")
            folder_button.clicked.connect(
                lambda checked=False, path=file_path: (
                    self.open_recent_artwork_folder(path)
                )
            )

            shortcut_widget = self.create_shortcut_widget(
                pixiv_button,
                folder_button,
            )

            table.setCellWidget(row, 3, shortcut_widget)
