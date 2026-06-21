from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
)


class ArtistArtworkSectionMixin:
    def _create_artwork_layout(self) -> QHBoxLayout:
        artwork_layout = QHBoxLayout()
        artwork_layout.setSpacing(12)

        artwork_layout.addWidget(self._create_missing_artwork_frame(), 1)
        artwork_layout.addWidget(self._create_recent_local_artwork_frame(), 1)
        artwork_layout.addWidget(self._create_tag_frame(), 1)

        return artwork_layout

    def _create_missing_artwork_frame(self) -> QFrame:
        missing_frame = QFrame()
        missing_frame.setObjectName("infoFrame")

        missing_layout = QVBoxLayout(missing_frame)
        missing_layout.setContentsMargins(16, 16, 16, 16)
        missing_layout.setSpacing(8)

        missing_header_layout = QHBoxLayout()

        self.missing_artwork_count_label = QLabel("누락 작품 ID 목록")
        self.missing_artwork_count_label.setObjectName("sectionTitle")

        self.open_all_missing_artwork_button = QPushButton("전체 Pixiv 열기")
        self.open_all_missing_artwork_button.setObjectName("artworkButton")

        missing_header_layout.addWidget(self.missing_artwork_count_label)
        missing_header_layout.addStretch()
        missing_header_layout.addWidget(self.open_all_missing_artwork_button)

        self.missing_artwork_table = QTableWidget()
        self.missing_artwork_table.setColumnCount(2)
        self.missing_artwork_table.setHorizontalHeaderLabels(
            ["작품 ID", "동작"]
        )
        self._setup_base_table(self.missing_artwork_table)
        self.missing_artwork_table.setFixedHeight(330)
        self.missing_artwork_table.setColumnWidth(0, 130)
        self.missing_artwork_table.setColumnWidth(1, 80)

        missing_layout.addLayout(missing_header_layout)
        missing_layout.addWidget(self.missing_artwork_table)

        return missing_frame

    def _create_recent_local_artwork_frame(self) -> QFrame:
        recent_frame = QFrame()
        recent_frame.setObjectName("infoFrame")

        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(16, 16, 16, 16)
        recent_layout.setSpacing(8)

        recent_header_layout = QHBoxLayout()

        recent_label = QLabel("최근 로컬 작품")
        recent_label.setObjectName("sectionTitle")

        recent_header_layout.addWidget(recent_label)
        recent_header_layout.addStretch()

        self.recent_local_artwork_table = QTableWidget()
        self.recent_local_artwork_table.setColumnCount(4)
        self.recent_local_artwork_table.setHorizontalHeaderLabels(
            ["작품 ID", "파일 수", "최근 변경일", "바로가기"]
        )
        self._setup_base_table(self.recent_local_artwork_table)
        self.recent_local_artwork_table.setFixedHeight(330)

        recent_header = self.recent_local_artwork_table.horizontalHeader()
        recent_header.setSectionResizeMode(0, QHeaderView.Stretch)
        recent_header.setSectionResizeMode(1, QHeaderView.Fixed)
        recent_header.setSectionResizeMode(2, QHeaderView.Fixed)
        recent_header.setSectionResizeMode(3, QHeaderView.Fixed)

        self.recent_local_artwork_table.setColumnWidth(1, 50)
        self.recent_local_artwork_table.setColumnWidth(2, 150)
        self.recent_local_artwork_table.setColumnWidth(3, 200)

        recent_layout.addLayout(recent_header_layout)
        recent_layout.addWidget(self.recent_local_artwork_table)

        return recent_frame

    def _create_tag_frame(self) -> QFrame:
        tag_frame = QFrame()
        tag_frame.setObjectName("infoFrame")

        tag_layout = QVBoxLayout(tag_frame)
        tag_layout.setContentsMargins(16, 16, 16, 16)
        tag_layout.setSpacing(8)

        tag_header_layout = QHBoxLayout()

        tag_label = QLabel("태그 통계")
        tag_label.setObjectName("sectionTitle")

        self.sort_tag_button = QPushButton("작품 수 정렬")
        self.clean_tag_button = QPushButton("태그 정리")
        self.add_tag_button = QPushButton("태그 추가")
        self.remove_tag_button = QPushButton("선택 삭제")

        tag_buttons = (
            self.sort_tag_button,
            self.clean_tag_button,
            self.add_tag_button,
            self.remove_tag_button,
        )

        for button in tag_buttons:
            button.setObjectName("tagButton")

        tag_header_layout.addWidget(tag_label)
        tag_header_layout.addStretch()
        tag_header_layout.addWidget(self.sort_tag_button)
        tag_header_layout.addWidget(self.clean_tag_button)
        tag_header_layout.addWidget(self.add_tag_button)
        tag_header_layout.addWidget(self.remove_tag_button)

        self.tag_table = QTableWidget()
        self.tag_table.setColumnCount(3)
        self.tag_table.setHorizontalHeaderLabels(
            ["태그 원문", "한글 번역", "작품 수"]
        )
        self._setup_base_table(self.tag_table)
        self.tag_table.setFixedHeight(330)

        self.tag_table.setColumnWidth(0, 150)
        self.tag_table.setColumnWidth(1, 150)
        self.tag_table.setColumnWidth(2, 70)

        tag_layout.addLayout(tag_header_layout)
        tag_layout.addWidget(self.tag_table)

        return tag_frame

    def _setup_base_table(
        self,
        table: QTableWidget,
    ):
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(30)
