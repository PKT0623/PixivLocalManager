from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..artist_table import UpdateArtistTable


class UpdateCheckTableFrameMixin:
    def _create_table_frame(self) -> QFrame:
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")

        frame_layout = QVBoxLayout(table_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_label = QLabel("작가 목록")
        title_label.setObjectName("sectionTitle")

        self.artist_table = UpdateArtistTable()

        frame_layout.addWidget(title_label)
        frame_layout.addWidget(self.artist_table, 1)

        return table_frame
