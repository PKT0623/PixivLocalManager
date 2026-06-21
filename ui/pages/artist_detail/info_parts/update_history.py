from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QVBoxLayout,
)


class ArtistUpdateHistoryMixin:
    def _create_update_history_frame(self) -> QFrame:
        update_history_frame = QFrame()
        update_history_frame.setObjectName("infoFrame")

        update_history_layout = QVBoxLayout(update_history_frame)
        update_history_layout.setContentsMargins(16, 16, 16, 16)
        update_history_layout.setSpacing(8)

        update_history_header_layout = QHBoxLayout()

        self.update_history_label = QLabel("업데이트 이력")
        self.update_history_label.setObjectName("sectionTitle")

        self.update_history_summary_label = QLabel("최근 누락 변화: -")
        self.update_history_summary_label.setObjectName("historySummaryLabel")

        update_history_header_layout.addWidget(self.update_history_label)
        update_history_header_layout.addStretch()
        update_history_header_layout.addWidget(
            self.update_history_summary_label
        )

        self.update_history_table = QTableWidget()
        self.update_history_table.setColumnCount(8)
        self.update_history_table.setHorizontalHeaderLabels(
            [
                "확인 시각",
                "결과",
                "로컬",
                "Pixiv",
                "누락",
                "변화",
                "신규/해결",
                "상세",
            ]
        )
        self._setup_update_history_table()

        update_history_layout.addLayout(update_history_header_layout)
        update_history_layout.addWidget(self.update_history_table)

        return update_history_frame

    def _setup_update_history_table(self):
        self.update_history_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.update_history_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.update_history_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.update_history_table.setAlternatingRowColors(True)
        self.update_history_table.verticalHeader().setVisible(False)
        self.update_history_table.verticalHeader().setDefaultSectionSize(30)
        self.update_history_table.setFixedHeight(300)

        update_history_header = self.update_history_table.horizontalHeader()
        update_history_header.setSectionResizeMode(0, QHeaderView.Fixed)
        update_history_header.setSectionResizeMode(1, QHeaderView.Fixed)
        update_history_header.setSectionResizeMode(2, QHeaderView.Fixed)
        update_history_header.setSectionResizeMode(3, QHeaderView.Fixed)
        update_history_header.setSectionResizeMode(4, QHeaderView.Fixed)
        update_history_header.setSectionResizeMode(5, QHeaderView.Fixed)
        update_history_header.setSectionResizeMode(6, QHeaderView.Fixed)
        update_history_header.setSectionResizeMode(7, QHeaderView.Stretch)

        self.update_history_table.setColumnWidth(0, 150)
        self.update_history_table.setColumnWidth(1, 100)
        self.update_history_table.setColumnWidth(2, 60)
        self.update_history_table.setColumnWidth(3, 60)
        self.update_history_table.setColumnWidth(4, 60)
        self.update_history_table.setColumnWidth(5, 90)
        self.update_history_table.setColumnWidth(6, 110)
