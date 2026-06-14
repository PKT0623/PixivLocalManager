from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
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

        self.last_viewed_at_label = QLabel("-")

        folder_layout = QHBoxLayout()
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setReadOnly(True)

        self.folder_select_button = QPushButton("폴더 선택")
        self.folder_select_button.setObjectName("folderSelectButton")

        folder_layout.addWidget(self.folder_path_input, 1)
        folder_layout.addWidget(self.folder_select_button)

        form_layout.addRow("작가명", self.artist_name_input)
        form_layout.addRow("Pixiv ID", self.pixiv_id_label)
        form_layout.addRow("작품 수", self.artwork_count_input)
        form_layout.addRow("파일 수", self.file_count_input)
        form_layout.addRow("평점", self.rating_input)
        form_layout.addRow("상태", self.status_label)
        form_layout.addRow("업데이트 상태", self.update_status_label)
        form_layout.addRow("메타데이터", metadata_layout)
        form_layout.addRow("최근 열람", self.last_viewed_at_label)
        form_layout.addRow("폴더 경로", folder_layout)

        tag_header_layout = QHBoxLayout()

        tag_label = QLabel("태그 통계")
        tag_label.setObjectName("sectionTitle")

        self.add_tag_button = QPushButton("태그 추가")
        self.add_tag_button.setObjectName("tagButton")

        self.remove_tag_button = QPushButton("선택 삭제")
        self.remove_tag_button.setObjectName("tagButton")

        tag_header_layout.addWidget(tag_label)
        tag_header_layout.addStretch()
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
        self.tag_table.setMinimumHeight(160)

        self.tag_table.setColumnWidth(0, 220)
        self.tag_table.setColumnWidth(1, 220)
        self.tag_table.setColumnWidth(2, 80)

        memo_label = QLabel("메모")
        memo_label.setObjectName("sectionTitle")

        self.memo_edit = QTextEdit()
        self.memo_edit.setMinimumHeight(120)

        layout.addWidget(form_frame)
        layout.addLayout(tag_header_layout)
        layout.addWidget(self.tag_table)
        layout.addWidget(memo_label)
        layout.addWidget(self.memo_edit)

    def add_empty_tag_row(self):
        row = self.tag_table.rowCount()
        self.tag_table.insertRow(row)

        self.tag_table.setItem(row, 0, QTableWidgetItem(""))
        self.tag_table.setItem(row, 1, QTableWidgetItem(""))
        self.tag_table.setItem(row, 2, QTableWidgetItem("0"))
