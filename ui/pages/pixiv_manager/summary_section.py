from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class PixivManagerSummarySection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("summaryFrame")
        self.labels = {}

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(8)

        title_label = QLabel("요약")
        title_label.setObjectName("sectionTitle")

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)

        self.labels["follow_total"] = self._create_summary_item(
            summary_layout,
            "팔로우 수",
        )
        self.labels["follow_matched"] = self._create_summary_item(
            summary_layout,
            "팔로우 매칭",
        )
        self.labels["follow_unmatched"] = self._create_summary_item(
            summary_layout,
            "팔로우 미매칭",
        )
        self.labels["bookmark_total"] = self._create_summary_item(
            summary_layout,
            "북마크 수",
        )
        self.labels["bookmark_matched"] = self._create_summary_item(
            summary_layout,
            "북마크 매칭",
        )
        self.labels["bookmark_unmatched"] = self._create_summary_item(
            summary_layout,
            "북마크 미매칭",
        )

        layout.addWidget(title_label)
        layout.addLayout(summary_layout)

    def _create_summary_item(
        self,
        parent_layout: QHBoxLayout,
        title: str,
    ) -> QLabel:
        item_frame = QFrame()
        item_frame.setObjectName("summaryItemFrame")

        item_layout = QVBoxLayout(item_frame)
        item_layout.setContentsMargins(14, 10, 14, 10)
        item_layout.setSpacing(4)

        value_label = QLabel("0")
        value_label.setObjectName("summaryValueLabel")

        title_label = QLabel(title)
        title_label.setObjectName("summaryTextLabel")

        item_layout.addWidget(value_label)
        item_layout.addWidget(title_label)

        parent_layout.addWidget(item_frame, 1)

        return value_label

    def update_summary(self, summary: dict):
        for key, label in self.labels.items():
            label.setText(str(summary.get(key, 0)))
