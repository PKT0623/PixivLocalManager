from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .formatters import format_bytes, format_count


class StatisticsTrendSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("sectionPanel")
        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 16, 18, 18)
        root_layout.setSpacing(10)

        title_label = QLabel("주간 변화")
        title_label.setObjectName("sectionTitle")

        description_label = QLabel(
            "주간별 누락 작품 증가량, 해결 작품 증가량, "
            "전체 용량 증가량을 표시합니다."
        )
        description_label.setObjectName("sectionSummaryLabel")
        description_label.setWordWrap(True)

        self.weekly_change_table = self._create_table()

        root_layout.addWidget(title_label)
        root_layout.addWidget(description_label)
        root_layout.addWidget(self.weekly_change_table, 1)

    def update_trend(
        self,
        trend: dict,
    ):
        self._update_weekly_change_table(
            trend.get("weekly_change", [])
        )

    def _update_weekly_change_table(
        self,
        rows: list[dict],
    ):
        self.weekly_change_table.setRowCount(0)

        for row_data in rows:
            row = self.weekly_change_table.rowCount()
            self.weekly_change_table.insertRow(row)

            self.weekly_change_table.setItem(
                row,
                0,
                self._create_item(row_data.get("week", "-")),
            )
            self.weekly_change_table.setItem(
                row,
                1,
                self._create_item(
                    format_count(
                        row_data.get("missing_increase_count", 0)
                    )
                ),
            )
            self.weekly_change_table.setItem(
                row,
                2,
                self._create_item(
                    format_count(
                        row_data.get("resolved_increase_count", 0)
                    )
                ),
            )
            self.weekly_change_table.setItem(
                row,
                3,
                self._create_item(
                    format_bytes(
                        row_data.get("folder_size_increase_bytes", 0)
                    )
                ),
            )

    def _create_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            [
                "주차",
                "누락 작품 증가",
                "해결 작품 증가",
                "저장 용량 증가",
            ]
        )
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        return table

    def _create_item(
        self,
        value,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        return item
