from PySide6.QtWidgets import QGridLayout

from .summary_card import SummaryCard


class SummarySection(QGridLayout):
    SUMMARY_ITEMS = [
        ("total_artists", "전체 작가", "0", 0, 0),
        ("favorite_artists", "즐겨찾기", "0", 0, 1),
        ("follow_users", "팔로우", "0", 0, 2),
        ("bookmark_artworks", "북마크", "0", 0, 3),
        ("need_update_count", "업데이트 필요", "0", 0, 4),
        ("error_count", "오류 작가", "0", 1, 0),
        ("total_artworks", "전체 작품 수", "0", 1, 1),
        ("total_files", "전체 파일 수", "0", 1, 2),
        ("total_folder_size", "전체 폴더 용량", "0 B", 1, 3),
        ("recent_scan", "최근 스캔", "-", 1, 4),
    ]

    def __init__(self):
        super().__init__()

        self.setSpacing(10)
        self.summary_labels = {}

        self._setup_ui()

    def _setup_ui(self):
        for item in self.SUMMARY_ITEMS:
            key, title, default_value, row, column = item

            self._add_summary_card(
                row=row,
                column=column,
                key=key,
                title=title,
                value=default_value,
            )

    def _add_summary_card(
        self,
        row: int,
        column: int,
        key: str,
        title: str,
        value: str,
    ):
        card = SummaryCard(
            title=title,
            value=value,
        )

        self.summary_labels[key] = card
        self.addWidget(card, row, column)

    def update_summary(self, summary: dict):
        for key, card in self.summary_labels.items():
            card.set_value(summary.get(key, "-"))
