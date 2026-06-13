import random
import re
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.artist_service import ArtistService


class DashboardPage(QWidget):
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    def __init__(self):
        super().__init__()

        self.artist_service = ArtistService()
        self.summary_labels = {}
        self.current_artists = []

        self.recent_artist_limit = 10
        self.recent_artist_limit_buttons = {}
        self.recent_artist_table = None
        self.recent_scan_label = None

        self.recommendation_limit = 10
        self.recommendation_limit_buttons = {}
        self.recommendation_layout = None

        self.random_artist = None
        self.random_status_label = None
        self.random_folder_button = None
        self.random_pixiv_button = None

        self._setup_ui()
        self.load_dashboard()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        title_label = QLabel("대시보드")
        title_label.setObjectName("pageTitle")

        description_label = QLabel("전체 작가 상태와 수집 현황을 요약해서 보여주는 화면입니다.")
        description_label.setObjectName("pageDescription")

        title_box.addWidget(title_label)
        title_box.addWidget(description_label)

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_dashboard)

        header_layout.addLayout(title_box, 1)
        header_layout.addWidget(self.refresh_button)

        summary_grid = QGridLayout()
        summary_grid.setSpacing(16)

        self._add_summary_card(summary_grid, 0, 0, "total_artists", "전체 작가", "0")
        self._add_summary_card(summary_grid, 0, 1, "total_artworks", "총 작품 수", "0")
        self._add_summary_card(summary_grid, 0, 2, "average_rating", "평균 평점", "-")
        self._add_summary_card(summary_grid, 1, 0, "unknown_count", "미확인", "0")
        self._add_summary_card(summary_grid, 1, 1, "latest_count", "최신", "0")
        self._add_summary_card(summary_grid, 1, 2, "need_update_count", "업데이트 필요", "0")

        detail_layout = QHBoxLayout()
        detail_layout.setSpacing(16)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(16)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)

        left_layout.addWidget(self._create_recent_artist_frame(), 1)
        left_layout.addWidget(self._create_recommendation_frame(), 1)

        right_layout.addWidget(self._create_recent_scan_frame())
        right_layout.addWidget(self._create_random_artist_frame(), 1)

        detail_layout.addLayout(left_layout, 2)
        detail_layout.addLayout(right_layout, 1)

        layout.addLayout(header_layout)
        layout.addLayout(summary_grid)
        layout.addLayout(detail_layout, 1)

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

            QPushButton {
                padding: 7px 12px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#refreshButton,
            QPushButton#limitButton {
                min-width: 58px;
            }

            QPushButton#limitButton[active="true"] {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
            }

            QFrame#summaryCard,
            QFrame#detailCard,
            QFrame#artistCard,
            QFrame#randomCard {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
            }

            QLabel#cardTitle {
                font-size: 14px;
                color: #666666;
                font-weight: 600;
            }

            QLabel#cardValue {
                font-size: 30px;
                font-weight: 800;
                color: #202124;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#subText {
                font-size: 13px;
                color: #777777;
            }

            QLabel#recentScanValue {
                font-size: 18px;
                font-weight: 700;
                color: #202124;
            }

            QLabel#thumbnailLabel {
                background-color: #f1f3f5;
                border: 1px solid #dddddd;
                border-radius: 8px;
                color: #777777;
            }

            QLabel#artistName {
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#artistInfo {
                font-size: 13px;
                color: #555555;
            }

            QLabel#randomHiddenText {
                font-size: 18px;
                font-weight: 800;
                color: #202124;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QTableWidget {
                border: none;
                background-color: #ffffff;
                gridline-color: #eeeeee;
                font-size: 14px;
            }

            QHeaderView::section {
                background-color: #f5f5f5;
                border: none;
                border-bottom: 1px solid #dddddd;
                padding: 8px;
                font-weight: 700;
            }

            QTableWidget::item {
                padding: 4px;
            }
            """
        )

    def load_dashboard(self):
        artists = self.artist_service.get_all_artists()
        self.current_artists = artists

        summary = self._calculate_summary(artists)

        self.summary_labels["total_artists"].setText(str(summary["total_artists"]))
        self.summary_labels["total_artworks"].setText(str(summary["total_artworks"]))
        self.summary_labels["average_rating"].setText(summary["average_rating"])
        self.summary_labels["unknown_count"].setText(str(summary["unknown_count"]))
        self.summary_labels["latest_count"].setText(str(summary["latest_count"]))
        self.summary_labels["need_update_count"].setText(str(summary["need_update_count"]))

        self._set_recent_artists(artists)
        self._set_recent_scan_time(artists)
        self._set_recommendations(artists)
        self._clear_random_artist()

    def _add_summary_card(
        self,
        grid: QGridLayout,
        row: int,
        column: int,
        key: str,
        title: str,
        value: str,
    ):
        card = QFrame()
        card.setObjectName("summaryCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        self.summary_labels[key] = value_label
        grid.addWidget(card, row, column)

    def _create_recent_artist_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("detailCard")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()

        title_label = QLabel("최근 등록 작가")
        title_label.setObjectName("sectionTitle")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        for limit in (10, 20, 50):
            button = QPushButton(str(limit))
            button.setObjectName("limitButton")
            button.clicked.connect(
                lambda checked=False, value=limit: self._set_recent_artist_limit(value)
            )

            self.recent_artist_limit_buttons[limit] = button
            button_layout.addWidget(button)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)

        self.recent_artist_table = QTableWidget()
        self.recent_artist_table.setColumnCount(5)
        self.recent_artist_table.setHorizontalHeaderLabels(
            ["No", "작가명", "Pixiv ID", "작품 수", "등록일"]
        )
        self.recent_artist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recent_artist_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.recent_artist_table.verticalHeader().setVisible(False)
        self.recent_artist_table.setShowGrid(True)
        self.recent_artist_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.recent_artist_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        header = self.recent_artist_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)

        self.recent_artist_table.setColumnWidth(0, 50)
        self.recent_artist_table.setColumnWidth(2, 120)
        self.recent_artist_table.setColumnWidth(3, 80)
        self.recent_artist_table.setColumnWidth(4, 150)
        self.recent_artist_table.verticalHeader().setDefaultSectionSize(30)
        self.recent_artist_table.setMinimumHeight(260)

        layout.addLayout(header_layout)
        layout.addWidget(self.recent_artist_table, 1)

        self._update_recent_artist_limit_buttons()

        return frame

    def _create_recent_scan_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("detailCard")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title_label = QLabel("최근 스캔 일시")
        title_label.setObjectName("sectionTitle")

        self.recent_scan_label = QLabel("-")
        self.recent_scan_label.setObjectName("recentScanValue")
        self.recent_scan_label.setWordWrap(True)

        sub_label = QLabel("last_checked_at 기준")
        sub_label.setObjectName("subText")

        layout.addWidget(title_label)
        layout.addWidget(self.recent_scan_label)
        layout.addWidget(sub_label)
        layout.addStretch()

        return frame

    def _create_recommendation_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("detailCard")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title_label = QLabel("작가 추천")
        title_label.setObjectName("sectionTitle")

        sub_label = QLabel("평점 8점 이상 작가 중 랜덤으로 추천합니다.")
        sub_label.setObjectName("subText")

        title_box.addWidget(title_label)
        title_box.addWidget(sub_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        for limit in (10, 20, 50):
            button = QPushButton(str(limit))
            button.setObjectName("limitButton")
            button.clicked.connect(
                lambda checked=False, value=limit: self._set_recommendation_limit(value)
            )

            self.recommendation_limit_buttons[limit] = button
            button_layout.addWidget(button)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.recommendation_layout = QHBoxLayout(scroll_content)
        self.recommendation_layout.setContentsMargins(0, 0, 0, 0)
        self.recommendation_layout.setSpacing(12)

        scroll_area.setWidget(scroll_content)

        layout.addLayout(header_layout)
        layout.addWidget(scroll_area, 1)

        self._update_recommendation_limit_buttons()

        return frame

    def _create_random_artist_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("detailCard")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()

        title_label = QLabel("랜덤 작가")
        title_label.setObjectName("sectionTitle")

        random_button = QPushButton("랜덤 선택")
        random_button.clicked.connect(self._select_random_artist)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(random_button)

        random_card = QFrame()
        random_card.setObjectName("randomCard")

        card_layout = QVBoxLayout(random_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        hidden_label = QLabel("???")
        hidden_label.setObjectName("randomHiddenText")
        hidden_label.setAlignment(Qt.AlignCenter)

        self.random_status_label = QLabel("아직 선택된 작가가 없습니다.")
        self.random_status_label.setObjectName("subText")
        self.random_status_label.setAlignment(Qt.AlignCenter)
        self.random_status_label.setWordWrap(True)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.random_folder_button = QPushButton("폴더 열기")
        self.random_pixiv_button = QPushButton("Pixiv 열기")

        self.random_folder_button.setEnabled(False)
        self.random_pixiv_button.setEnabled(False)

        self.random_folder_button.clicked.connect(self._open_random_folder)
        self.random_pixiv_button.clicked.connect(self._open_random_pixiv)

        button_layout.addWidget(self.random_folder_button)
        button_layout.addWidget(self.random_pixiv_button)

        card_layout.addStretch()
        card_layout.addWidget(hidden_label)
        card_layout.addWidget(self.random_status_label)
        card_layout.addLayout(button_layout)
        card_layout.addStretch()

        layout.addLayout(header_layout)
        layout.addWidget(random_card, 1)

        return frame

    def _calculate_summary(self, artists: list[dict]) -> dict:
        total_artists = len(artists)
        total_artworks = sum(
            self._to_int(artist.get("folder_artwork_count", 0))
            for artist in artists
        )

        rating_values = [
            self._to_int(artist.get("rating", 0), minimum=0, maximum=10)
            for artist in artists
            if self._to_int(artist.get("rating", 0), minimum=0, maximum=10) > 0
        ]

        average_rating = (
            f"{sum(rating_values) / len(rating_values):.1f}"
            if rating_values
            else "-"
        )

        return {
            "total_artists": total_artists,
            "total_artworks": total_artworks,
            "average_rating": average_rating,
            "unknown_count": self._count_status(artists, {"unknown"}),
            "latest_count": self._count_status(artists, {"latest", "up_to_date"}),
            "need_update_count": self._count_status(artists, {"need_update"}),
        }

    def _count_status(self, artists: list[dict], statuses: set[str]) -> int:
        return sum(
            1
            for artist in artists
            if str(artist.get("update_status", "")) in statuses
        )

    def _set_recent_artist_limit(self, limit: int):
        self.recent_artist_limit = limit
        self._update_recent_artist_limit_buttons()
        self._set_recent_artists(self.current_artists)

    def _set_recommendation_limit(self, limit: int):
        self.recommendation_limit = limit
        self._update_recommendation_limit_buttons()
        self._set_recommendations(self.current_artists)

    def _update_recent_artist_limit_buttons(self):
        for limit, button in self.recent_artist_limit_buttons.items():
            is_active = limit == self.recent_artist_limit
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def _update_recommendation_limit_buttons(self):
        for limit, button in self.recommendation_limit_buttons.items():
            is_active = limit == self.recommendation_limit
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def _set_recent_artists(self, artists: list[dict]):
        sorted_artists = sorted(
            artists,
            key=lambda artist: str(artist.get("created_at", "") or ""),
            reverse=True,
        )

        recent_artists = sorted_artists[: self.recent_artist_limit]
        self.recent_artist_table.setRowCount(self.recent_artist_limit)

        for row in range(self.recent_artist_limit):
            if row >= len(recent_artists):
                values = ["-", "-", "-", "-", "-"]
            else:
                artist = recent_artists[row]
                values = [
                    str(row + 1),
                    str(artist.get("artist_name", "") or "-"),
                    str(artist.get("pixiv_id", "") or "-"),
                    str(self._to_int(artist.get("folder_artwork_count", 0))),
                    self._format_datetime_short(artist.get("created_at")),
                ]

            for column, value in enumerate(values):
                self._set_table_item(row, column, value)

    def _set_table_item(self, row: int, column: int, text: str):
        item = QTableWidgetItem(text)

        if column in (0, 2, 3, 4):
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.recent_artist_table.setItem(row, column, item)

    def _set_recent_scan_time(self, artists: list[dict]):
        scan_times = [
            str(artist.get("last_checked_at", "") or "")
            for artist in artists
            if artist.get("last_checked_at")
        ]

        if not scan_times:
            self.recent_scan_label.setText("-")
            return

        self.recent_scan_label.setText(
            self._format_datetime(max(scan_times))
        )

    def _set_recommendations(self, artists: list[dict]):
        self._clear_layout(self.recommendation_layout)

        high_rated_artists = [
            artist
            for artist in artists
            if self._to_int(artist.get("rating", 0), maximum=10) >= 8
        ]

        recommendations = random.sample(
            high_rated_artists,
            min(self.recommendation_limit, len(high_rated_artists)),
        )

        if not recommendations:
            empty_label = QLabel("평점 8점 이상 추천 대상 작가가 없습니다.")
            empty_label.setObjectName("subText")
            self.recommendation_layout.addWidget(empty_label)
            return

        for artist in recommendations:
            self.recommendation_layout.addWidget(
                self._create_artist_recommend_card(artist)
            )

        self.recommendation_layout.addStretch()

    def _create_artist_recommend_card(self, artist: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("artistCard")
        card.setFixedWidth(190)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        thumbnail = QLabel("이미지 없음")
        thumbnail.setObjectName("thumbnailLabel")
        thumbnail.setAlignment(Qt.AlignCenter)
        thumbnail.setFixedSize(160, 110)

        image_path = self._find_latest_p0_image(artist.get("folder_path"))
        if image_path:
            pixmap = QPixmap(str(image_path))
            thumbnail.setPixmap(
                pixmap.scaled(
                    thumbnail.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        name_label = QLabel(str(artist.get("artist_name", "") or "-"))
        name_label.setObjectName("artistName")
        name_label.setWordWrap(True)

        info_label = QLabel(
            f"평점 {self._to_int(artist.get('rating', 0), maximum=10)}"
            f" / 작품 {self._to_int(artist.get('folder_artwork_count', 0))}"
        )
        info_label.setObjectName("artistInfo")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        folder_button = QPushButton("폴더")
        pixiv_button = QPushButton("Pixiv")

        folder_button.clicked.connect(
            lambda checked=False, target=artist: self._open_artist_folder(target)
        )
        pixiv_button.clicked.connect(
            lambda checked=False, target=artist: self._open_artist_pixiv(target)
        )

        pixiv_button.setEnabled(bool(str(artist.get("pixiv_id", "") or "").strip()))

        button_layout.addWidget(folder_button)
        button_layout.addWidget(pixiv_button)

        layout.addWidget(thumbnail, alignment=Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(info_label)
        layout.addLayout(button_layout)

        return card

    def _select_random_artist(self):
        if not self.current_artists:
            self.random_artist = None
            self.random_status_label.setText("선택할 작가가 없습니다.")
            self.random_folder_button.setEnabled(False)
            self.random_pixiv_button.setEnabled(False)
            return

        self.random_artist = random.choice(self.current_artists)
        self.random_status_label.setText(
            "랜덤 작가가 선택되었습니다.\n정체를 확인하려면 열어보세요."
        )
        self.random_folder_button.setEnabled(True)
        self.random_pixiv_button.setEnabled(
            bool(str(self.random_artist.get("pixiv_id", "") or "").strip())
        )

    def _clear_random_artist(self):
        self.random_artist = None

        if self.random_status_label is None:
            return

        self.random_status_label.setText("아직 선택된 작가가 없습니다.")
        self.random_folder_button.setEnabled(False)
        self.random_pixiv_button.setEnabled(False)

    def _open_random_folder(self):
        if self.random_artist is None:
            return

        self._open_artist_folder(self.random_artist)

    def _open_random_pixiv(self):
        if self.random_artist is None:
            return

        self._open_artist_pixiv(self.random_artist)

    def _open_artist_folder(self, artist: dict):
        folder_path = str(artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    def _open_artist_pixiv(self, artist: dict):
        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        QDesktopServices.openUrl(QUrl(f"https://www.pixiv.net/users/{pixiv_id}"))

    def _find_latest_p0_image(self, folder_path):
        if not folder_path:
            return None

        folder = Path(folder_path)

        if not folder.exists() or not folder.is_dir():
            return None

        candidates = []

        for file_path in folder.iterdir():
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in self.IMAGE_EXTENSIONS:
                continue

            match = re.search(r"(\d+)_p0", file_path.name)

            if match is None:
                continue

            candidates.append((int(match.group(1)), file_path))

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0], reverse=True)

        return candidates[0][1]

    def _format_datetime(self, value) -> str:
        if value is None or value == "":
            return "-"

        text = str(value)

        try:
            dt = datetime.fromisoformat(text)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return text

    def _format_datetime_short(self, value) -> str:
        if value is None or value == "":
            return "-"

        text = str(value)

        try:
            dt = datetime.fromisoformat(text)
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return text

    def _to_int(self, value, minimum: int = 0, maximum: int = 999999) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = minimum

        return max(minimum, min(maximum, number))

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()
