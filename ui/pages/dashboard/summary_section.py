from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class SummarySection(QGridLayout):
    def __init__(self):
        super().__init__()

        self.setSpacing(16)
        self.summary_labels = {}

        self._setup_ui()

    def _setup_ui(self):
        self._add_summary_card(0, 0, "total_artists", "전체 작가", "0")
        self._add_summary_card(0, 1, "total_artworks", "총 작품 수", "0")
        self._add_summary_card(0, 2, "average_rating", "평균 평점", "-")
        self._add_summary_card(1, 0, "unknown_count", "미확인", "0")
        self._add_summary_card(1, 1, "latest_count", "최신", "0")
        self._add_summary_card(1, 2, "need_update_count", "업데이트 필요", "0")

    def _add_summary_card(
        self,
        row: int,
        column: int,
        key: str,
        title: str,
        value: str,
    ):
        card = QFrame()
        card.setObjectName("summaryCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        self.summary_labels[key] = value_label
        self.addWidget(card, row, column)

    def update_summary(self, summary: dict):
        self.summary_labels["total_artists"].setText(str(summary["total_artists"]))
        self.summary_labels["total_artworks"].setText(str(summary["total_artworks"]))
        self.summary_labels["average_rating"].setText(summary["average_rating"])
        self.summary_labels["unknown_count"].setText(str(summary["unknown_count"]))
        self.summary_labels["latest_count"].setText(str(summary["latest_count"]))
        self.summary_labels["need_update_count"].setText(
            str(summary["need_update_count"])
        )
