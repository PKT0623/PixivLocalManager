from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ArtistsToolbar(QWidget):
    def __init__(self):
        super().__init__()

        self.rating_filter_mode = "min"

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "작가명 또는 Pixiv ID 검색"
        )

        self.rating_toggle_button = QPushButton("평점: 별")
        self.update_check_button = QPushButton("업데이트 확인")
        self.refresh_button = QPushButton("새로고침")

        top_layout.addWidget(self.search_input, 1)
        top_layout.addWidget(self.rating_toggle_button)
        top_layout.addWidget(self.update_check_button)
        top_layout.addWidget(self.refresh_button)

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(30)

        self.rating_filter_input = QLineEdit()
        self.rating_filter_input.setPlaceholderText("1~10")
        self.rating_filter_input.setFixedWidth(80)
        self.rating_filter_input.setAlignment(Qt.AlignCenter)
        self.rating_filter_input.setValidator(
            QIntValidator(1, 10)
        )
        self.rating_filter_input.textChanged.connect(
            self.normalize_rating_filter_input
        )

        self.rating_filter_mode_button = QPushButton("이상")
        self.rating_filter_mode_button.setFixedWidth(70)

        self.favorite_only_checkbox = QCheckBox("즐겨찾기")
        self.update_required_only_checkbox = QCheckBox("업데이트 필요")
        self.unknown_only_checkbox = QCheckBox("미확인")
        self.unrated_only_checkbox = QCheckBox("평점 미설정")

        self.exclude_hidden_checkbox = QCheckBox("숨김 제외")
        self.exclude_hidden_checkbox.setChecked(False)

        self.reset_filter_button = QPushButton("필터 초기화")
        self.reset_sort_button = QPushButton("정렬 초기화")

        filter_layout.addWidget(self.rating_filter_input)
        filter_layout.addWidget(self.rating_filter_mode_button)
        filter_layout.addWidget(self.favorite_only_checkbox)
        filter_layout.addWidget(self.update_required_only_checkbox)
        filter_layout.addWidget(self.unknown_only_checkbox)
        filter_layout.addWidget(self.unrated_only_checkbox)
        filter_layout.addWidget(self.exclude_hidden_checkbox)
        filter_layout.addWidget(self.reset_filter_button)
        filter_layout.addWidget(self.reset_sort_button)
        filter_layout.addStretch()

        main_layout.addLayout(top_layout)
        main_layout.addLayout(filter_layout)

    def normalize_rating_filter_input(self):
        text = self.rating_filter_input.text().strip()

        if not text:
            return

        try:
            rating = int(text)
        except ValueError:
            self.rating_filter_input.clear()
            return

        if rating < 1:
            self.rating_filter_input.setText("1")
        elif rating > 10:
            self.rating_filter_input.setText("10")

    def get_rating_filter_value(self) -> int:
        text = self.rating_filter_input.text().strip()

        if not text:
            return 0

        return int(text)

    def get_rating_filter_mode(self) -> str:
        return self.rating_filter_mode

    def toggle_rating_filter_mode(self):
        if self.rating_filter_mode == "min":
            self.rating_filter_mode = "exact"
            self.rating_filter_mode_button.setText("일치")
        else:
            self.rating_filter_mode = "min"
            self.rating_filter_mode_button.setText("이상")

    def reset_filter_values(self):
        widgets = (
            self.search_input,
            self.rating_filter_input,
            self.favorite_only_checkbox,
            self.update_required_only_checkbox,
            self.unknown_only_checkbox,
            self.unrated_only_checkbox,
            self.exclude_hidden_checkbox,
        )

        for widget in widgets:
            widget.blockSignals(True)

        self.search_input.clear()
        self.rating_filter_input.clear()
        self.favorite_only_checkbox.setChecked(False)
        self.update_required_only_checkbox.setChecked(False)
        self.unknown_only_checkbox.setChecked(False)
        self.unrated_only_checkbox.setChecked(False)
        self.exclude_hidden_checkbox.setChecked(False)

        for widget in widgets:
            widget.blockSignals(False)

        self.rating_filter_mode = "min"
        self.rating_filter_mode_button.setText("이상")
