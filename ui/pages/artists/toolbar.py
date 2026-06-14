from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class ArtistsToolbar(QWidget):
    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "작가명 또는 Pixiv ID 검색"
        )

        self.rating_toggle_button = QPushButton("평점: 별")
        self.update_check_button = QPushButton("업데이트 확인")
        self.refresh_button = QPushButton("새로고침")

        layout.addWidget(self.search_input, 1)
        layout.addWidget(self.rating_toggle_button)
        layout.addWidget(self.update_check_button)
        layout.addWidget(self.refresh_button)
