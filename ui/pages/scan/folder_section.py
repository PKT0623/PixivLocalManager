from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class ScanFolderSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("inputFrame")

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        folder_label = QLabel("스캔할 폴더")
        folder_label.setObjectName("sectionTitle")

        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(8)

        self.folder_path_input = QLineEdit()
        self.folder_path_input.setReadOnly(True)
        self.folder_path_input.setPlaceholderText(
            "폴더를 선택하세요."
        )

        self.folder_select_button = QPushButton("폴더 선택")
        self.folder_select_button.setObjectName(
            "folderSelectButton"
        )

        self.scan_button = QPushButton("스캔 및 등록")
        self.scan_button.setObjectName("scanButton")

        folder_layout.addWidget(
            self.folder_path_input,
            1,
        )
        folder_layout.addWidget(
            self.folder_select_button
        )
        folder_layout.addWidget(
            self.scan_button
        )

        layout.addWidget(folder_label)
        layout.addLayout(folder_layout)
