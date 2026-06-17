from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class StatisticsRatingSection(QWidget):
    def __init__(self):
        super().__init__()

        self.rating_rows = {}

        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("sectionPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title_label = QLabel("평점 분포")
        title_label.setObjectName("sectionTitle")

        self.summary_label = QLabel("-")
        self.summary_label.setObjectName("sectionSummaryLabel")

        layout.addWidget(title_label)
        layout.addWidget(self.summary_label)

        for rating in range(10, -1, -1):
            row = self._create_distribution_row(f"{rating}점")
            self.rating_rows[rating] = row

            layout.addWidget(row["widget"])

        layout.addStretch()

    def _create_distribution_row(self, label_text: str) -> dict:
        widget = QFrame()
        widget.setObjectName("distributionRow")

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        label = QLabel(label_text)
        label.setObjectName("distributionNameLabel")
        label.setFixedWidth(60)

        progress = QProgressBar()
        progress.setObjectName("ratingProgress")
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setTextVisible(False)

        value_label = QLabel("0명")
        value_label.setObjectName("distributionValueLabel")
        value_label.setFixedWidth(48)

        layout.addWidget(label)
        layout.addWidget(progress, 1)
        layout.addWidget(value_label)

        return {
            "widget": widget,
            "progress": progress,
            "value_label": value_label,
        }

    def update_rating(self, rating_data: dict):
        distribution = rating_data.get("rating_distribution", {})
        rated_count = self._to_int(rating_data.get("rated_count", 0))
        unrated_count = self._to_int(rating_data.get("unrated_count", 0))

        total_count = sum(
            self._to_int(value)
            for value in distribution.values()
        )

        self.summary_label.setText(
            f"평점 입력 {rated_count:,}명 / "
            f"미설정 {unrated_count:,}명"
        )

        for rating, row in self.rating_rows.items():
            count = self._to_int(distribution.get(rating, 0))
            ratio = self._calculate_ratio(count, total_count)

            row["progress"].setValue(int(round(ratio)))
            row["value_label"].setText(f"{count:,}명")

    def _calculate_ratio(self, count: int, total_count: int) -> float:
        if total_count <= 0:
            return 0.0

        return count / total_count * 100

    def _to_int(self, value) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
