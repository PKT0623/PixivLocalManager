from PySide6.QtWidgets import (
    QFrame,
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
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("기본 폴더")
        title_label.setObjectName("sectionTitle")

        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)

        self.pixiv_root_input = QLineEdit()
        self.pixiv_root_input.setReadOnly(True)
        self.pixiv_root_input.setPlaceholderText("기본 Pixiv 폴더를 선택하세요.")

        self.select_pixiv_root_button = QPushButton("폴더 선택")
        self.save_pixiv_root_button = QPushButton("저장")
        self.save_pixiv_root_button.setObjectName("primaryButton")

        row_layout.addWidget(self.pixiv_root_input, 1)
        row_layout.addWidget(self.select_pixiv_root_button)
        row_layout.addWidget(self.save_pixiv_root_button)

        layout.addWidget(title_label)
        layout.addLayout(row_layout)
