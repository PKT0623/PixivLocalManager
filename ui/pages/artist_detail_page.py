from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.services.artist_service import ArtistService


class ArtistDetailPage(QWidget):
    back_requested = Signal()

    STATUS_LABELS = {
        "active": "활성",
        "inactive": "비활성",
        "unknown": "미확인",
        "latest": "최신",
        "up_to_date": "최신",
        "need_update": "업데이트 필요",
        "updated": "업데이트 완료",
        "error": "오류",
    }

    def __init__(self):
        super().__init__()

        self.artist_id = None
        self.artist_service = ArtistService()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()

        self.title_label = QLabel("작가 상세")
        self.title_label.setObjectName("pageTitle")

        self.back_button = QPushButton("← 작가 목록")
        self.back_button.setObjectName("backButton")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.back_button)

        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")

        form_layout = QFormLayout(info_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)

        self.artist_name_label = QLabel("-")
        self.pixiv_id_label = QLabel("-")
        self.artwork_count_label = QLabel("-")
        self.rating_label = QLabel("-")
        self.status_label = QLabel("-")
        self.update_status_label = QLabel("-")

        self.folder_path_input = QLineEdit()
        self.folder_path_input.setReadOnly(True)

        form_layout.addRow("작가명", self.artist_name_label)
        form_layout.addRow("Pixiv ID", self.pixiv_id_label)
        form_layout.addRow("작품 수", self.artwork_count_label)
        form_layout.addRow("평점", self.rating_label)
        form_layout.addRow("상태", self.status_label)
        form_layout.addRow("업데이트 상태", self.update_status_label)
        form_layout.addRow("폴더 경로", self.folder_path_input)

        memo_label = QLabel("메모")
        memo_label.setObjectName("sectionTitle")

        self.memo_edit = QTextEdit()
        self.memo_edit.setReadOnly(True)
        self.memo_edit.setMinimumHeight(120)

        layout.addLayout(header_layout)
        layout.addWidget(info_frame)
        layout.addWidget(memo_label)
        layout.addWidget(self.memo_edit)
        layout.addStretch()

        self.setStyleSheet(
            """
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
                margin-top: 8px;
            }

            QFrame#infoFrame {
                border: 1px solid #dddddd;
                border-radius: 8px;
                background-color: #ffffff;
            }

            QPushButton#backButton {
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }

            QPushButton#backButton:hover {
                background-color: #eeeeee;
            }

            QLineEdit {
                border: 1px solid #dddddd;
                border-radius: 6px;
                padding: 6px 8px;
                background-color: #f9f9f9;
                font-size: 14px;
            }

            QTextEdit {
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 8px;
                background-color: #ffffff;
                font-size: 14px;
            }
            """
        )

    def _connect_signals(self):
        self.back_button.clicked.connect(self.back_requested.emit)

    def set_artist(self, artist_id: int):
        self.artist_id = artist_id

        artist = self.artist_service.get_artist(artist_id)

        if artist is None:
            self._clear_artist()
            return

        self._set_artist_data(artist)

    def _set_artist_data(self, artist: dict):
        self.artist_name_label.setText(
            self._display_value(artist.get("artist_name"))
        )
        self.pixiv_id_label.setText(
            self._display_value(artist.get("pixiv_id"))
        )
        self.artwork_count_label.setText(
            self._display_value(
                artist.get("folder_artwork_count", 0)
            )
        )
        self.rating_label.setText(
            self._format_rating(artist.get("rating", 0))
        )
        self.status_label.setText(
            self._status_label(artist.get("status"))
        )
        self.update_status_label.setText(
            self._status_label(artist.get("update_status"))
        )
        self.folder_path_input.setText(
            self._display_value(artist.get("folder_path"))
        )
        self.memo_edit.setPlainText(
            str(artist.get("memo", "") or "")
        )

    def _clear_artist(self):
        self.artist_name_label.setText("-")
        self.pixiv_id_label.setText("-")
        self.artwork_count_label.setText("-")
        self.rating_label.setText("-")
        self.status_label.setText("-")
        self.update_status_label.setText("-")
        self.folder_path_input.setText("-")
        self.memo_edit.clear()

    def _display_value(self, value) -> str:
        if value is None or value == "":
            return "-"

        return str(value)

    def _status_label(self, value) -> str:
        if value is None or value == "":
            return "-"

        return self.STATUS_LABELS.get(str(value), str(value))

    def _format_rating(self, value) -> str:
        try:
            rating = int(value)
        except (TypeError, ValueError):
            rating = 0

        rating = max(0, min(10, rating))

        stars = self._rating_to_stars(rating)

        return f"{stars} ({rating}/10)"

    def _rating_to_stars(self, rating: int) -> str:
        if rating <= 0:
            return "-"

        full_stars = rating // 2
        has_half_score = rating % 2 == 1

        stars = "★" * full_stars

        if has_half_score:
            stars += "☆"

        return stars
