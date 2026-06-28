from ...utils import (
    calculate_missing_artwork_ids,
    parse_id_text,
)


class ArtworkMissingTableMixin:
    def set_missing_artwork_table_data(self, artist: dict):
        section = self.page.info_section
        table = section.missing_artwork_table
        table.setRowCount(0)

        local_ids = parse_id_text(
            artist.get("local_latest_artwork_ids", "")
        )
        pixiv_ids = parse_id_text(
            artist.get("pixiv_latest_artwork_ids", "")
        )
        missing_ids = calculate_missing_artwork_ids(
            local_ids,
            pixiv_ids,
        )

        section.missing_artwork_count_label.setText(
            f"누락 작품 ID 목록 ({len(missing_ids)}개)"
        )

        for artwork_id in missing_ids:
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(
                row,
                0,
                self.create_readonly_item(artwork_id),
            )

            pixiv_button = self.create_small_button("이동")
            pixiv_button.clicked.connect(
                lambda checked=False, aid=artwork_id: (
                    self.open_pixiv_artwork(aid)
                )
            )

            table.setCellWidget(
                row,
                1,
                self.create_centered_widget(pixiv_button),
            )
