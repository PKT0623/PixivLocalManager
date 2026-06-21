from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)


class UpdateCheckSummaryFrameMixin:
    def _create_summary_frame(self) -> QFrame:
        summary_frame = QFrame()
        summary_frame.setObjectName("summaryFrame")

        frame_layout = QVBoxLayout(summary_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_label = QLabel("결과 요약")
        title_label.setObjectName("sectionTitle")

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)

        self.summary_total_label = self._create_summary_item(
            summary_layout,
            "총 확인",
        )
        self.summary_latest_label = self._create_summary_item(
            summary_layout,
            "최신",
        )
        self.summary_need_update_label = self._create_summary_item(
            summary_layout,
            "업데이트 필요",
        )
        self.summary_error_label = self._create_summary_item(
            summary_layout,
            "오류",
        )
        self.summary_skipped_label = self._create_summary_item(
            summary_layout,
            "스킵",
        )
        self.summary_missing_label = self._create_summary_item(
            summary_layout,
            "누락 합계",
        )

        frame_layout.addWidget(title_label)
        frame_layout.addLayout(summary_layout)

        return summary_frame

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
