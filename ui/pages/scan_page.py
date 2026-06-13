from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ScanPage(QWidget):
    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)

        title_label = QLabel("폴더 스캔")
        title_label.setObjectName("pageTitle")

        description_label = QLabel("Pixiv 이미지 폴더를 선택하고 파일명을 분석해 DB에 등록하는 화면입니다.")
        description_label.setObjectName("pageDescription")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()

        self.setStyleSheet(
            """
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#pageDescription {
                font-size: 15px;
                color: #666666;
            }
            """
        )
