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
        self.pixiv_id_label = QLabel("-")
        self.artwork_count_input = QLineEdit()
        self.file_count_input = QLineEdit()
        self.rating_input = QLineEdit()
        self.status_label = QLabel("-")
        self.update_status_label = QLabel("-")

        self.artwork_count_input.setPlaceholderText("0 이상의 정수")
        self.file_count_input.setPlaceholderText("0 이상의 정수")
        self.rating_input.setPlaceholderText("0~10")

        pixiv_id_layout = self._create_pixiv_id_layout()
        metadata_layout = self._create_metadata_layout()
        self._create_datetime_labels()
        folder_layout = self._create_folder_layout()

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

        return form_frame

    def _create_pixiv_id_layout(self) -> QHBoxLayout:
        pixiv_id_layout = QHBoxLayout()

        self.copy_pixiv_id_button = QPushButton("복사")
        self.copy_pixiv_id_button.setObjectName("copyButton")

        pixiv_id_layout.addWidget(self.pixiv_id_label, 1)
        pixiv_id_layout.addWidget(self.copy_pixiv_id_button)

        return pixiv_id_layout

    def _create_metadata_layout(self) -> QHBoxLayout:
        self.favorite_checkbox = QCheckBox("즐겨찾기")
        self.hidden_checkbox = QCheckBox("숨김")

        metadata_layout = QHBoxLayout()
        metadata_layout.addWidget(self.favorite_checkbox)
        metadata_layout.addWidget(self.hidden_checkbox)
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

        self.folder_path_input = QLineEdit()
        self.folder_path_input.setReadOnly(True)

        self.copy_folder_path_button = QPushButton("복사")
        self.copy_folder_path_button.setObjectName("copyButton")

        self.folder_select_button = QPushButton("폴더 선택")
        self.folder_select_button.setObjectName("folderSelectButton")

        folder_layout.addWidget(self.folder_path_input, 1)
        folder_layout.addWidget(self.copy_folder_path_button)
        folder_layout.addWidget(self.folder_select_button)

        return folder_layout
