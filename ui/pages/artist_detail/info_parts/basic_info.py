from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class ArtistBasicInfoMixin:
    def _create_basic_info_frame(self) -> QFrame:
        form_frame = QFrame()
        form_frame.setObjectName("infoFrame")

        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)

        self.artist_name_input = QLineEdit()
        self.artist_name_input.setFixedWidth(200)

        self.pixiv_id_label = QLabel("-")

        self.artwork_count_input = QLineEdit()
        self.artwork_count_input.setFixedWidth(90)

        self.file_count_input = QLineEdit()
        self.file_count_input.setFixedWidth(90)

        self.folder_size_label = QLabel("-")

        self.rating_input = QLineEdit()
        self.rating_input.setFixedWidth(90)

        self.status_label = QLabel("-")
        self.update_status_label = QLabel("-")

        self.artwork_count_input.setPlaceholderText("0 이상의 정수")
        self.file_count_input.setPlaceholderText("0 이상의 정수")
        self.rating_input.setPlaceholderText("0~10")

        artist_name_layout = self._create_artist_name_layout()
        pixiv_id_layout = self._create_pixiv_id_layout()
        metadata_layout = self._create_metadata_layout()
        self._create_datetime_labels()
        folder_layout = self._create_folder_layout()

        form_layout.addRow("작가명", artist_name_layout)
        form_layout.addRow("Pixiv ID", pixiv_id_layout)
        form_layout.addRow("작품 수", self.artwork_count_input)
        form_layout.addRow("파일 수", self.file_count_input)
        form_layout.addRow("저장 용량", self.folder_size_label)
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

        return form_frame

    def _create_artist_name_layout(self) -> QHBoxLayout:
        artist_name_layout = QHBoxLayout()
        artist_name_layout.setContentsMargins(0, 0, 0, 0)
        artist_name_layout.setSpacing(8)

        self.open_folder_button = QPushButton("폴더 열기")
        self.open_folder_button.setObjectName("shortcutButton")

        self.open_pixiv_button = QPushButton("Pixiv 열기")
        self.open_pixiv_button.setObjectName("shortcutButton")

        artist_name_layout.addWidget(self.artist_name_input)
        artist_name_layout.addStretch()
        artist_name_layout.addWidget(self.open_folder_button)
        artist_name_layout.addWidget(self.open_pixiv_button)

        return artist_name_layout

    def _create_pixiv_id_layout(self) -> QHBoxLayout:
        pixiv_id_layout = QHBoxLayout()
        pixiv_id_layout.setContentsMargins(0, 0, 0, 0)
        pixiv_id_layout.setSpacing(8)

        self.copy_pixiv_id_button = QPushButton("복사")
        self.copy_pixiv_id_button.setObjectName("copyButton")

        pixiv_id_layout.addWidget(self.pixiv_id_label)
        pixiv_id_layout.addWidget(self.copy_pixiv_id_button)
        pixiv_id_layout.addStretch()

        return pixiv_id_layout

    def _create_metadata_layout(self) -> QHBoxLayout:
        self.favorite_checkbox = QCheckBox("즐겨찾기")

        metadata_layout = QHBoxLayout()
        metadata_layout.addWidget(self.favorite_checkbox)
        metadata_layout.addStretch()

        return metadata_layout

    def _create_datetime_labels(self):
        self.last_checked_at_label = QLabel("-")
        self.last_viewed_at_label = QLabel("-")
        self.created_at_label = QLabel("-")
        self.updated_at_label = QLabel("-")
        self.folder_status_label = QLabel("-")

    def _create_folder_layout(self) -> QHBoxLayout:
        folder_layout = QHBoxLayout()
        folder_layout.setContentsMargins(0, 0, 0, 0)
        folder_layout.setSpacing(8)

        self.folder_path_input = QLineEdit()
        self.folder_path_input.setReadOnly(True)

        self.folder_select_button = QPushButton("폴더 선택")
        self.folder_select_button.setObjectName("folderSelectButton")

        folder_layout.addWidget(self.folder_path_input, 1)
        folder_layout.addWidget(self.folder_select_button)

        return folder_layout
