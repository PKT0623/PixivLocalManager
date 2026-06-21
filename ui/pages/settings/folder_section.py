from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class FolderSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self.extension_checkboxes = {}

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel("기본 폴더")
        title_label.setObjectName("sectionTitle")

        folder_row_layout = QHBoxLayout()
        folder_row_layout.setSpacing(8)

        self.pixiv_root_input = QLineEdit()
        self.pixiv_root_input.setReadOnly(True)
        self.pixiv_root_input.setPlaceholderText("기본 Pixiv 폴더를 선택하세요.")

        self.select_pixiv_root_button = QPushButton("폴더 선택")
        self.save_pixiv_root_button = QPushButton("저장")
        self.save_pixiv_root_button.setObjectName("primaryButton")

        folder_row_layout.addWidget(self.pixiv_root_input, 1)
        folder_row_layout.addWidget(self.select_pixiv_root_button)
        folder_row_layout.addWidget(self.save_pixiv_root_button)

        scan_title_label = QLabel("스캔 설정")
        scan_title_label.setObjectName("sectionTitle")

        extension_description_label = QLabel(
            "작품 파일로 인식할 이미지 확장자를 선택하세요."
        )
        extension_description_label.setObjectName("infoText")

        extension_layout = QGridLayout()
        extension_layout.setHorizontalSpacing(12)
        extension_layout.setVerticalSpacing(8)

        extension_items = [
            ("jpg", "JPG"),
            ("jpeg", "JPEG"),
            ("png", "PNG"),
            ("gif", "GIF"),
            ("webp", "WEBP"),
            ("bmp", "BMP"),
        ]

        for index, item in enumerate(extension_items):
            extension, label = item
            checkbox = self._create_extension_checkbox(label)

            self.extension_checkboxes[extension] = checkbox
            extension_layout.addWidget(
                checkbox,
                index // 3,
                index % 3,
            )

        extension_button_layout = QHBoxLayout()
        extension_button_layout.setSpacing(8)

        self.save_scan_extensions_button = QPushButton("확장자 저장")
        self.save_scan_extensions_button.setObjectName("primaryButton")
        self.reset_scan_extensions_button = QPushButton("기본값 복원")

        extension_button_layout.addStretch()
        extension_button_layout.addWidget(self.reset_scan_extensions_button)
        extension_button_layout.addWidget(self.save_scan_extensions_button)

        self.scan_extensions_status_label = QLabel("현재 기본값 사용 중")
        self.scan_extensions_status_label.setObjectName("infoText")

        layout.addWidget(title_label)
        layout.addLayout(folder_row_layout)
        layout.addWidget(scan_title_label)
        layout.addWidget(extension_description_label)
        layout.addLayout(extension_layout)
        layout.addLayout(extension_button_layout)
        layout.addWidget(self.scan_extensions_status_label)

    def _create_extension_checkbox(
        self,
        text: str,
    ):
        from PySide6.QtWidgets import QCheckBox

        checkbox = QCheckBox(text)
        checkbox.setChecked(True)

        return checkbox

    def set_scan_image_extensions(
        self,
        extensions: list[str],
    ):
        normalized_extensions = {
            str(extension or "").strip().lower().lstrip(".")
            for extension in extensions
        }

        for extension, checkbox in self.extension_checkboxes.items():
            checkbox.setChecked(extension in normalized_extensions)

        self.update_scan_extensions_status(extensions)

    def get_scan_image_extensions(self) -> list[str]:
        extensions = []

        for extension, checkbox in self.extension_checkboxes.items():
            if checkbox.isChecked():
                extensions.append(extension)

        return extensions

    def update_scan_extensions_status(
        self,
        extensions: list[str],
    ):
        normalized_extensions = [
            str(extension or "").strip().lower().lstrip(".")
            for extension in extensions
            if str(extension or "").strip()
        ]

        if not normalized_extensions:
            self.scan_extensions_status_label.setText(
                "현재 선택된 확장자 없음"
            )
            return

        self.scan_extensions_status_label.setText(
            "현재 작품 파일 확장자: "
            + ", ".join(normalized_extensions)
        )
