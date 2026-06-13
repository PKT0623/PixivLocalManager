from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.services.artist_service import ArtistService


class ArtistDetailPage(QWidget):
    back_requested = Signal()
    artist_updated = Signal(int)

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
        self.current_artist = None
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

        self.save_button = QPushButton("저장")
        self.save_button.setObjectName("saveButton")

        self.back_button = QPushButton("← 작가 목록")
        self.back_button.setObjectName("backButton")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.back_button)

        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")

        form_layout = QFormLayout(info_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)

        self.artist_name_input = QLineEdit()

        self.pixiv_id_label = QLabel("-")

        self.artwork_count_input = QLineEdit()
        self.artwork_count_input.setPlaceholderText("0 이상의 정수")

        self.rating_input = QLineEdit()
        self.rating_input.setPlaceholderText("0~10")

        self.status_label = QLabel("-")
        self.update_status_label = QLabel("-")

        folder_layout = QHBoxLayout()
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setReadOnly(True)

        self.folder_select_button = QPushButton("폴더 선택")
        self.folder_select_button.setObjectName("folderSelectButton")

        folder_layout.addWidget(self.folder_path_input, 1)
        folder_layout.addWidget(self.folder_select_button)

        form_layout.addRow("작가명", self.artist_name_input)
        form_layout.addRow("Pixiv ID", self.pixiv_id_label)
        form_layout.addRow("작품 수", self.artwork_count_input)
        form_layout.addRow("평점", self.rating_input)
        form_layout.addRow("상태", self.status_label)
        form_layout.addRow("업데이트 상태", self.update_status_label)
        form_layout.addRow("폴더 경로", folder_layout)

        memo_label = QLabel("메모")
        memo_label.setObjectName("sectionTitle")

        self.memo_edit = QTextEdit()
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

            QPushButton#backButton,
            QPushButton#saveButton,
            QPushButton#folderSelectButton {
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#saveButton {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
                min-width: 80px;
            }

            QPushButton#backButton {
                min-width: 120px;
            }

            QPushButton#folderSelectButton {
                min-width: 100px;
            }

            QPushButton#backButton:hover,
            QPushButton#folderSelectButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#saveButton:hover {
                background-color: #157347;
            }

            QLineEdit {
                border: 1px solid #dddddd;
                border-radius: 6px;
                padding: 6px 8px;
                background-color: #ffffff;
                font-size: 14px;
            }

            QLineEdit:read-only {
                background-color: #f9f9f9;
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
        self.save_button.clicked.connect(self._save_artist)
        self.folder_select_button.clicked.connect(self._select_folder)

    def set_artist(self, artist_id: int):
        self.artist_id = artist_id

        artist = self.artist_service.get_artist(artist_id)

        if artist is None:
            self._clear_artist()
            return

        self.current_artist = artist
        self._set_artist_data(artist)

    def _set_artist_data(self, artist: dict):
        self.artist_name_input.setText(
            self._display_value(artist.get("artist_name"))
        )
        self.pixiv_id_label.setText(
            self._display_value(artist.get("pixiv_id"))
        )
        self.artwork_count_input.setText(
            str(self._to_int(artist.get("folder_artwork_count", 0)))
        )
        self.rating_input.setText(
            str(self._to_int(artist.get("rating", 0), minimum=0, maximum=10))
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
        self.artist_id = None
        self.current_artist = None

        self.artist_name_input.clear()
        self.pixiv_id_label.setText("-")
        self.artwork_count_input.clear()
        self.rating_input.clear()
        self.status_label.setText("-")
        self.update_status_label.setText("-")
        self.folder_path_input.clear()
        self.memo_edit.clear()

    def _select_folder(self):
        current_path = self.folder_path_input.text().strip()

        if current_path == "-":
            current_path = ""

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "작가 폴더 선택",
            current_path,
        )

        if not folder_path:
            return

        self.folder_path_input.setText(folder_path)

    def _save_artist(self):
        if self.artist_id is None or self.current_artist is None:
            self._show_warning(
                "저장 오류",
                "저장할 작가 정보가 없습니다.",
            )
            return

        artist_name = self.artist_name_input.text().strip()

        if not artist_name:
            self._show_warning(
                "입력 오류",
                "작가명은 비워둘 수 없습니다.",
            )
            return

        try:
            artwork_count = self._parse_non_negative_int(
                self.artwork_count_input.text(),
                "작품 수",
            )
            rating = self._parse_rating(
                self.rating_input.text(),
            )
        except ValueError as error:
            self._show_warning(
                "입력 오류",
                str(error),
            )
            return

        folder_path = self.folder_path_input.text().strip()

        if folder_path == "-":
            folder_path = ""

        update_data = dict(self.current_artist)
        update_data["artist_name"] = artist_name
        update_data["folder_artwork_count"] = artwork_count
        update_data["rating"] = rating
        update_data["memo"] = self.memo_edit.toPlainText().strip()
        update_data["folder_path"] = folder_path

        try:
            self.artist_service.update_artist(
                self.artist_id,
                update_data,
            )
        except Exception as error:
            self._show_warning(
                "저장 오류",
                f"작가 정보를 저장하지 못했습니다.\n{error}",
            )
            return

        self.current_artist = update_data
        self.artist_updated.emit(self.artist_id)

        self._show_information(
            "저장 완료",
            "작가 정보가 저장되었습니다.",
        )

    def _parse_non_negative_int(self, value: str, field_label: str) -> int:
        value = value.strip()

        if not value:
            raise ValueError(f"{field_label}는 비워둘 수 없습니다.")

        try:
            number = int(value)
        except ValueError as error:
            raise ValueError(f"{field_label}는 0 이상의 정수여야 합니다.") from error

        if number < 0:
            raise ValueError(f"{field_label}는 0 이상의 정수여야 합니다.")

        return number

    def _parse_rating(self, value: str) -> int:
        rating = self._parse_non_negative_int(value, "평점")

        if rating > 10:
            raise ValueError("평점은 0부터 10까지의 정수여야 합니다.")

        return rating

    def _show_information(self, title: str, message: str):
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.NoIcon)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()

    def _show_warning(self, title: str, message: str):
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.NoIcon)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()

    def _display_value(self, value) -> str:
        if value is None or value == "":
            return "-"

        return str(value)

    def _status_label(self, value) -> str:
        if value is None or value == "":
            return "-"

        return self.STATUS_LABELS.get(str(value), str(value))

    def _to_int(self, value, minimum: int = 0, maximum: int = 999999) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = minimum

        return max(minimum, min(maximum, number))
