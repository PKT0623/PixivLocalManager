from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class StatisticsStatusSection(QWidget):
    STATUS_ORDER = [
        "up_to_date",
        "need_update",
        "unknown",
        "error",
    ]

    DEFAULT_LABELS = {
        "up_to_date": "최신 상태",
        "need_update": "업데이트 필요",
        "unknown": "미확인",
        "error": "오류",
    }

    def __init__(self):
        super().__init__()

        self.status_rows = {}

        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("sectionPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        title_label = QLabel("상태 분포")
        title_label.setObjectName("sectionTitle")

        layout.addWidget(title_label)

        for status in self.STATUS_ORDER:
            row = self._create_status_row(status)
            self.status_rows[status] = row

            layout.addWidget(row["widget"])

        layout.addStretch()

    def _create_status_row(self, status: str) -> dict:
        widget = QFrame()
        widget.setObjectName("statusRow")

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        label = QLabel(self.DEFAULT_LABELS.get(status, status))
        label.setObjectName("statusNameLabel")
        label.setFixedWidth(90)

        progress = QProgressBar()
        progress.setObjectName(f"statusProgress_{status}")
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setTextVisible(False)

        value_label = QLabel("0명 / 0.0%")
        value_label.setObjectName("statusValueLabel")
        value_label.setFixedWidth(86)

        layout.addWidget(label)
        layout.addWidget(progress, 1)
        layout.addWidget(value_label)

        return {
            "widget": widget,
            "label": label,
            "progress": progress,
            "value_label": value_label,
        }

    def update_status(self, status_data: dict):
        counts = status_data.get("counts", {})
        ratios = status_data.get("ratios", {})
        labels = status_data.get("labels", {})

        for status in self.STATUS_ORDER:
            row = self.status_rows.get(status)

            if row is None:
                continue

            count = self._to_int(counts.get(status, 0))
            ratio = self._to_float(ratios.get(status, 0))
            label = labels.get(
                status,
                self.DEFAULT_LABELS.get(status, status),
            )

            row["label"].setText(label)
            row["progress"].setValue(int(round(ratio)))
            row["value_label"].setText(f"{count:,}명 / {ratio:.1f}%")

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
