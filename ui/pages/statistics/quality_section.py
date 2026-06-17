from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class StatisticsQualitySection(QWidget):
    QUALITY_ITEMS = [
        {
            "key": "rating",
            "title": "평점 입력률",
            "input_count": "rating_input_count",
            "empty_count": "unrated_count",
            "ratio": "rating_input_ratio",
            "empty_label": "미설정",
        },
        {
            "key": "tag",
            "title": "태그 입력률",
            "input_count": "tag_input_count",
            "empty_count": "untagged_count",
            "ratio": "tag_input_ratio",
            "empty_label": "태그 없음",
        },
        {
            "key": "memo",
            "title": "메모 입력률",
            "input_count": "memo_input_count",
            "empty_count": "memo_empty_count",
            "ratio": "memo_input_ratio",
            "empty_label": "메모 없음",
        },
    ]

    def __init__(self):
        super().__init__()

        self.rows = {}

        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("sectionPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title_label = QLabel("데이터 품질")
        title_label.setObjectName("sectionTitle")

        layout.addWidget(title_label)

        for item in self.QUALITY_ITEMS:
            row = self._create_quality_row(item)
            self.rows[item["key"]] = row
            layout.addWidget(row["widget"])

        layout.addStretch()

    def _create_quality_row(self, item: dict) -> dict:
        widget = QFrame()
        widget.setObjectName("qualityRow")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_label = QLabel(item["title"])
        title_label.setObjectName("qualityTitleLabel")

        value_label = QLabel("-")
        value_label.setObjectName("qualityValueLabel")

        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(value_label)

        progress = QProgressBar()
        progress.setObjectName("qualityProgress")
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setTextVisible(False)

        detail_label = QLabel("-")
        detail_label.setObjectName("qualityDetailLabel")

        layout.addLayout(header_layout)
        layout.addWidget(progress)
        layout.addWidget(detail_label)

        return {
            "widget": widget,
            "value_label": value_label,
            "progress": progress,
            "detail_label": detail_label,
        }

    def update_quality(self, quality_data: dict):
        total_count = self._to_int(quality_data.get("total_count", 0))

        for item in self.QUALITY_ITEMS:
            row = self.rows.get(item["key"])

            if row is None:
                continue

            input_count = self._to_int(
                quality_data.get(item["input_count"], 0)
            )
            empty_count = self._to_int(
                quality_data.get(item["empty_count"], 0)
            )
            ratio = self._to_float(
                quality_data.get(item["ratio"], 0)
            )

            row["value_label"].setText(f"{ratio:.1f}%")
            row["progress"].setValue(int(round(ratio)))
            row["detail_label"].setText(
                f"입력 {input_count:,}명 / "
                f"{item['empty_label']} {empty_count:,}명 / "
                f"전체 {total_count:,}명"
            )

    def _to_int(self, value) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _to_float(self, value) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
