from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
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

        self.rating_input = QLineEdit()
        self.rating_input.setPlaceholderText("0~10")

        self.status_label = QLabel("-")
        self.update_status_label = QLabel("-")

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
        form_layout.addRow("평점", self.rating_input)
        form_layout.addRow("상태", self.status_label)
        form_layout.addRow("업데이트 상태", self.update_status_label)
        form_layout.addRow("폴더 경로", folder_layout)

        memo_label = QLabel("메모")
        memo_label.setObjectName("sectionTitle")

        self.memo_edit = QTextEdit()
        self.memo_edit.setMinimumHeight(120)

        layout.addWidget(form_frame)
        layout.addWidget(memo_label)
        layout.addWidget(self.memo_edit)
