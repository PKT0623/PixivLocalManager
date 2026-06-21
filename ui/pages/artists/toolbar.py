from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
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

        self.search_mode_combo = QComboBox()
        self.search_mode_combo.addItem("전체 검색", "all")
        self.search_mode_combo.addItem("작가명", "artist_name")
        self.search_mode_combo.addItem("Pixiv ID", "pixiv_id")
        self.search_mode_combo.addItem("태그", "tags")
        self.search_mode_combo.setFixedWidth(140)
        self.search_mode_combo.setFixedHeight(34)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어 입력")

        self.rating_toggle_button = QPushButton("평점: 별")
        self.refresh_button = QPushButton("새로고침")

        top_layout.addWidget(self.search_mode_combo)
        top_layout.addWidget(self.search_input, 1)
        top_layout.addWidget(self.rating_toggle_button)
        top_layout.addWidget(self.refresh_button)

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(8)

        rating_filter_widget = QWidget()
        rating_filter_widget.setFixedWidth(210)

        rating_filter_layout = QHBoxLayout(rating_filter_widget)
        rating_filter_layout.setContentsMargins(0, 0, 0, 0)
        rating_filter_layout.setSpacing(6)

        rating_label = QLabel("평점")
        rating_label.setFixedWidth(40)

        rating_label_font = rating_label.font()
        rating_label_font.setPointSize(10)
        rating_label_font.setBold(True)
        rating_label.setFont(rating_label_font)

        self.rating_filter_input = QLineEdit()
        self.rating_filter_input.setPlaceholderText("1~10")
        self.rating_filter_input.setFixedWidth(72)
        self.rating_filter_input.setAlignment(Qt.AlignCenter)
        self.rating_filter_input.setValidator(QIntValidator(1, 10))
        self.rating_filter_input.textChanged.connect(
            self.normalize_rating_filter_input
        )

        self.rating_filter_mode_button = QPushButton("이상")
        self.rating_filter_mode_button.setFixedWidth(62)

        rating_filter_layout.addWidget(rating_label)
        rating_filter_layout.addWidget(self.rating_filter_input)
        rating_filter_layout.addWidget(self.rating_filter_mode_button)

        self.favorite_only_checkbox = QCheckBox("즐겨찾기")
        self.update_required_only_checkbox = QCheckBox("업데이트 필요")
        self.unknown_only_checkbox = QCheckBox("미확인")
        self.unrated_only_checkbox = QCheckBox("평점 미설정")

        self.reset_filter_button = QPushButton("필터 초기화")
        self.reset_sort_button = QPushButton("정렬 초기화")
        self.restore_deleted_button = QPushButton("삭제 복구")

        filter_layout.addWidget(rating_filter_widget)
        filter_layout.addWidget(self.favorite_only_checkbox)
        filter_layout.addWidget(self.update_required_only_checkbox)
        filter_layout.addWidget(self.unknown_only_checkbox)
        filter_layout.addWidget(self.unrated_only_checkbox)
        filter_layout.addWidget(self.reset_filter_button)
        filter_layout.addWidget(self.reset_sort_button)
        filter_layout.addWidget(self.restore_deleted_button)
        filter_layout.addStretch()

        for button in (
            self.rating_toggle_button,
            self.refresh_button,
            self.rating_filter_mode_button,
            self.reset_filter_button,
            self.reset_sort_button,
            self.restore_deleted_button,
        ):
            button.setFixedHeight(34)

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

    def get_search_mode(self) -> str:
        return str(self.search_mode_combo.currentData() or "all")

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
            self.search_mode_combo,
            self.search_input,
            self.rating_filter_input,
            self.favorite_only_checkbox,
            self.update_required_only_checkbox,
            self.unknown_only_checkbox,
            self.unrated_only_checkbox,
        )

        for widget in widgets:
            widget.blockSignals(True)

        self.search_mode_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.rating_filter_input.clear()
        self.favorite_only_checkbox.setChecked(False)
        self.update_required_only_checkbox.setChecked(False)
        self.unknown_only_checkbox.setChecked(False)
        self.unrated_only_checkbox.setChecked(False)

        for widget in widgets:
            widget.blockSignals(False)

        self.rating_filter_mode = "min"
        self.rating_filter_mode_button.setText("이상")
