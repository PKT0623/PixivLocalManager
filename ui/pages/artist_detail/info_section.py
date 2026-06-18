from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)


class ArtistInfoSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("infoFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        form_frame = QFrame()
        form_frame.setObjectName("infoFrame")

        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)

        self.artist_name_input = QLineEdit()

        self.pixiv_id_label = QLabel("-")

        pixiv_id_layout = QHBoxLayout()
        self.copy_pixiv_id_button = QPushButton("복사")
        self.copy_pixiv_id_button.setObjectName("copyButton")

        pixiv_id_layout.addWidget(self.pixiv_id_label, 1)
        pixiv_id_layout.addWidget(self.copy_pixiv_id_button)

        self.artwork_count_input = QLineEdit()
        self.artwork_count_input.setPlaceholderText("0 이상의 정수")

        self.file_count_input = QLineEdit()
        self.file_count_input.setPlaceholderText("0 이상의 정수")

        self.rating_input = QLineEdit()
        self.rating_input.setPlaceholderText("0~10")

        self.status_label = QLabel("-")
        self.update_status_label = QLabel("-")

        self.favorite_checkbox = QCheckBox("즐겨찾기")
        self.hidden_checkbox = QCheckBox("숨김")

        metadata_layout = QHBoxLayout()
        metadata_layout.addWidget(self.favorite_checkbox)
        metadata_layout.addWidget(self.hidden_checkbox)
        metadata_layout.addStretch()

        self.last_checked_at_label = QLabel("-")
        self.last_viewed_at_label = QLabel("-")
        self.created_at_label = QLabel("-")
        self.updated_at_label = QLabel("-")
        self.folder_status_label = QLabel("-")

        folder_layout = QHBoxLayout()
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setReadOnly(True)

        self.copy_folder_path_button = QPushButton("복사")
        self.copy_folder_path_button.setObjectName("copyButton")

        self.folder_select_button = QPushButton("폴더 선택")
        self.folder_select_button.setObjectName("folderSelectButton")

        folder_layout.addWidget(self.folder_path_input, 1)
        folder_layout.addWidget(self.copy_folder_path_button)
        folder_layout.addWidget(self.folder_select_button)

        form_layout.addRow("작가명", self.artist_name_input)
        form_layout.addRow("Pixiv ID", pixiv_id_layout)
        form_layout.addRow("작품 수", self.artwork_count_input)
        form_layout.addRow("파일 수", self.file_count_input)
        form_layout.addRow("평점", self.rating_input)
        form_layout.addRow("상태", self.status_label)
        form_layout.addRow("업데이트 상태", self.update_status_label)
        form_layout.addRow("메타데이터", metadata_layout)
        form_layout.addRow("최근 확인", self.last_checked_at_label)
        form_layout.addRow("최근 열람", self.last_viewed_at_label)
        form_layout.addRow("생성일", self.created_at_label)
        form_layout.addRow("수정일", self.updated_at_label)
        form_layout.addRow("폴더 상태", self.folder_status_label)
        form_layout.addRow("폴더 경로", folder_layout)

        artwork_layout = QHBoxLayout()
        artwork_layout.setSpacing(12)

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
        self.missing_artwork_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.missing_artwork_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.missing_artwork_table.setAlternatingRowColors(True)
        self.missing_artwork_table.verticalHeader().setVisible(False)
        self.missing_artwork_table.verticalHeader().setDefaultSectionSize(30)
        self.missing_artwork_table.setFixedHeight(330)
        self.missing_artwork_table.setColumnWidth(0, 130)
        self.missing_artwork_table.setColumnWidth(1, 80)

        missing_layout.addLayout(missing_header_layout)
        missing_layout.addWidget(self.missing_artwork_table)

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
        self.recent_local_artwork_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.recent_local_artwork_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.recent_local_artwork_table.setAlternatingRowColors(True)
        self.recent_local_artwork_table.verticalHeader().setVisible(False)
        self.recent_local_artwork_table.verticalHeader().setDefaultSectionSize(
            30
        )
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

        tag_frame = QFrame()
        tag_frame.setObjectName("infoFrame")

        tag_layout = QVBoxLayout(tag_frame)
        tag_layout.setContentsMargins(16, 16, 16, 16)
        tag_layout.setSpacing(8)

        tag_header_layout = QHBoxLayout()

        tag_label = QLabel("태그 통계")
        tag_label.setObjectName("sectionTitle")

        self.sort_tag_button = QPushButton("작품 수 정렬")
        self.sort_tag_button.setObjectName("tagButton")

        self.clean_tag_button = QPushButton("태그 정리")
        self.clean_tag_button.setObjectName("tagButton")

        self.add_tag_button = QPushButton("태그 추가")
        self.add_tag_button.setObjectName("tagButton")

        self.remove_tag_button = QPushButton("선택 삭제")
        self.remove_tag_button.setObjectName("tagButton")

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
        self.tag_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tag_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tag_table.setAlternatingRowColors(True)
        self.tag_table.verticalHeader().setVisible(False)
        self.tag_table.verticalHeader().setDefaultSectionSize(30)
        self.tag_table.setFixedHeight(330)

        self.tag_table.setColumnWidth(0, 150)
        self.tag_table.setColumnWidth(1, 150)
        self.tag_table.setColumnWidth(2, 70)

        tag_layout.addLayout(tag_header_layout)
        tag_layout.addWidget(self.tag_table)

        artwork_layout.addWidget(missing_frame, 1)
        artwork_layout.addWidget(recent_frame, 1)
        artwork_layout.addWidget(tag_frame, 1)

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

        update_history_layout.addLayout(update_history_header_layout)
        update_history_layout.addWidget(self.update_history_table)

        memo_frame = QFrame()
        memo_frame.setObjectName("infoFrame")

        memo_layout = QVBoxLayout(memo_frame)
        memo_layout.setContentsMargins(16, 16, 16, 16)
        memo_layout.setSpacing(8)

        memo_label = QLabel("장문 메모")
        memo_label.setObjectName("sectionTitle")

        self.memo_edit = QTextEdit()
        self.memo_edit.setMinimumHeight(180)
        self.memo_edit.setPlaceholderText("작가에 대한 장문 메모를 입력하세요.")

        reference_links_label = QLabel("참고 링크")
        reference_links_label.setObjectName("sectionTitle")

        self.reference_links_edit = QTextEdit()
        self.reference_links_edit.setMinimumHeight(90)
        self.reference_links_edit.setPlaceholderText(
            "참고할 링크를 줄 단위로 입력하세요."
        )

        download_note_label = QLabel("다운로드 메모")
        download_note_label.setObjectName("sectionTitle")

        self.download_note_edit = QTextEdit()
        self.download_note_edit.setMinimumHeight(120)
        self.download_note_edit.setPlaceholderText(
            "다운로드 기준, 제외 조건, 주의사항 등을 입력하세요."
        )

        memo_layout.addWidget(memo_label)
        memo_layout.addWidget(self.memo_edit)
        memo_layout.addWidget(reference_links_label)
        memo_layout.addWidget(self.reference_links_edit)
        memo_layout.addWidget(download_note_label)
        memo_layout.addWidget(self.download_note_edit)

        layout.addWidget(form_frame)
        layout.addLayout(artwork_layout)
        layout.addWidget(update_history_frame)
        layout.addWidget(memo_frame)

    def add_empty_tag_row(self):
        row = self.tag_table.rowCount()
        self.tag_table.insertRow(row)

        original_item = QTableWidgetItem("")
        original_item.setFlags(
            original_item.flags()
            & ~Qt.ItemIsEditable
        )

        self.tag_table.setItem(row, 0, original_item)
        self.tag_table.setItem(row, 1, QTableWidgetItem(""))
        self.tag_table.setItem(row, 2, QTableWidgetItem("0"))
