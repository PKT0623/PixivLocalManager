from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
)


class UpdateStatusSection(QFrame):
    METRIC_ITEMS = [
        ("total_missing_count", "전체 누락", "0"),
        ("today_update_count", "오늘 확인", "0"),
        ("today_new_missing_count", "신규 누락", "0"),
        ("today_resolved_missing_count", "해결", "0"),
    ]

    STATUS_ITEMS = [
        ("latest_count", "최신"),
        ("need_update_count", "필요"),
        ("unknown_count", "미확인"),
        ("error_count", "실패"),
    ]

    def __init__(self):
        super().__init__()

        self.metric_labels = {}
        self.status_labels = {}

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(8)

        title_label = QLabel("업데이트 현황")
        title_label.setObjectName("sectionTitle")

        metric_layout = QGridLayout()
        metric_layout.setSpacing(6)

        for index, item in enumerate(self.METRIC_ITEMS):
            key, title, default_value = item
            self._add_metric_item(
                metric_layout,
                row=index // 2,
                column=index % 2,
                key=key,
                title=title,
                value=default_value,
            )

        status_title_label = QLabel("상태 분포")
        status_title_label.setObjectName("sectionSubTitle")

        status_layout = QGridLayout()
        status_layout.setSpacing(6)

        for index, item in enumerate(self.STATUS_ITEMS):
            key, title = item
            self._add_status_card(
                status_layout,
                row=index // 2,
                column=index % 2,
                key=key,
                title=title,
            )

        layout.addWidget(title_label)
        layout.addLayout(metric_layout)
        layout.addWidget(status_title_label)
        layout.addLayout(status_layout)

    def _add_metric_item(
        self,
        parent_layout: QGridLayout,
        row: int,
        column: int,
        key: str,
        title: str,
        value: str,
    ):
        item_frame = QFrame()
        item_frame.setObjectName("statusMetricCard")

        item_layout = QVBoxLayout(item_frame)
        item_layout.setContentsMargins(8, 6, 8, 6)
        item_layout.setSpacing(1)

        value_label = QLabel(value)
        value_label.setObjectName("statusMetricValue")
        value_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("statusMetricTitle")
        title_label.setAlignment(Qt.AlignCenter)

        item_layout.addWidget(value_label)
        item_layout.addWidget(title_label)

        self.metric_labels[key] = value_label
        parent_layout.addWidget(item_frame, row, column)

    def _add_status_card(
        self,
        parent_layout: QGridLayout,
        row: int,
        column: int,
        key: str,
        title: str,
    ):
        item_frame = QFrame()
        item_frame.setObjectName("statusMetricCard")

        item_layout = QVBoxLayout(item_frame)
        item_layout.setContentsMargins(8, 6, 8, 6)
        item_layout.setSpacing(1)

        value_label = QLabel("0")
        value_label.setObjectName("statusMetricValue")
        value_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("statusMetricTitle")
        title_label.setAlignment(Qt.AlignCenter)

        item_layout.addWidget(value_label)
        item_layout.addWidget(title_label)

        self.status_labels[key] = value_label
        parent_layout.addWidget(item_frame, row, column)

    def update_status_summary(self, summary: dict):
        for key, label in self.metric_labels.items():
            label.setText(str(summary.get(key, "0")))

        for key, label in self.status_labels.items():
            label.setText(str(summary.get(key, "0")))
