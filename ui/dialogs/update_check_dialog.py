import random
import time
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.services.artist_service import ArtistService


class UpdateCheckWorker(QObject):
    log_requested = Signal(dict)
    progress_updated = Signal(int, int)
    finished = Signal()
    failed = Signal(str)

    MIN_WAIT_SECONDS = 5
    MAX_WAIT_SECONDS = 10
    BATCH_SIZE = 20
    MIN_BATCH_REST_SECONDS = 180
    MAX_BATCH_REST_SECONDS = 300

    def __init__(self, artist_ids: list[int]):
        super().__init__()

        self.artist_ids = artist_ids
        self.artist_service = ArtistService()
        self.is_cancelled = False

    def run(self):
        total = len(self.artist_ids)

        try:
            for index, artist_id in enumerate(self.artist_ids, start=1):
                if self.is_cancelled:
                    self._emit_info(index, total, "취소됨", "작업이 취소되었습니다.")
                    break

                if index > 1:
                    self._safe_sleep(
                        random.uniform(
                            self.MIN_WAIT_SECONDS,
                            self.MAX_WAIT_SECONDS,
                        )
                    )

                try:
                    result = self.artist_service.check_artist_update(artist_id)
                    artist = result.get("artist") or {}

                    self.log_requested.emit(
                        {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "progress": f"{index}/{total}",
                            "result": self._status_label(result),
                            "artist_name": artist.get("artist_name", "-"),
                            "pixiv_id": artist.get("pixiv_id", "-"),
                            "local_count": result.get("local_count", "-"),
                            "pixiv_count": result.get("pixiv_count", "-"),
                            "missing_count": result.get("missing_count", "-"),
                            "status": result.get("status", "-"),
                        }
                    )
                except Exception as error:
                    error_message = str(error)

                    self.log_requested.emit(
                        {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "progress": f"{index}/{total}",
                            "result": "오류",
                            "artist_name": f"artist_id={artist_id}",
                            "pixiv_id": "-",
                            "local_count": "-",
                            "pixiv_count": "-",
                            "missing_count": "-",
                            "status": error_message,
                        }
                    )

                    if "HTTP 403" in error_message or "HTTP 429" in error_message:
                        self.failed.emit(
                            "Pixiv 요청 제한 가능성이 있어 작업을 중단했습니다."
                        )
                        return

                self.progress_updated.emit(index, total)

                if index % self.BATCH_SIZE == 0 and index < total:
                    rest_seconds = random.uniform(
                        self.MIN_BATCH_REST_SECONDS,
                        self.MAX_BATCH_REST_SECONDS,
                    )
                    self._emit_info(
                        index,
                        total,
                        "휴식",
                        f"{self.BATCH_SIZE}명 처리 완료. 잠시 대기합니다.",
                    )
                    self._safe_sleep(rest_seconds)

        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit()

    def cancel(self):
        self.is_cancelled = True

    def _safe_sleep(self, seconds: float):
        end_time = time.time() + seconds

        while time.time() < end_time:
            if self.is_cancelled:
                return

            time.sleep(0.5)

    def _emit_info(
        self,
        current: int,
        total: int,
        result: str,
        message: str,
    ):
        self.log_requested.emit(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": f"{current}/{total}",
                "result": result,
                "artist_name": message,
                "pixiv_id": "-",
                "local_count": "-",
                "pixiv_count": "-",
                "missing_count": "-",
                "status": "-",
            }
        )

    def _status_label(self, result: dict) -> str:
        status = result.get("status")

        if status == "need_update":
            return "업데이트 필요"

        if status == "up_to_date":
            return "최신"

        if status == "unknown":
            return "미확인"

        return "확인 완료"


class UpdateCheckDialog(QDialog):
    update_finished = Signal()

    RESULT_COLORS = {
        "최신": "#198754",
        "업데이트 필요": "#fd7e14",
        "미확인": "#6c757d",
        "오류": "#dc3545",
        "휴식": "#0d6efd",
        "취소됨": "#6c757d",
        "확인 완료": "#0d6efd",
    }

    def __init__(self, artists: list[dict], parent=None):
        super().__init__(parent)

        self.artists = artists
        self.artist_checkboxes = {}
        self.worker_thread = None
        self.worker = None

        self.setWindowTitle("Pixiv 업데이트 확인")
        self.resize(980, 720)

        self._setup_ui()
        self._connect_signals()
        self._load_artists()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_label = QLabel("Pixiv 업데이트 확인")
        title_label.setObjectName("dialogTitle")

        description_label = QLabel(
            "선택한 작가의 Pixiv 최신 작품 목록을 확인합니다. "
            "요청 간격은 안전을 위해 자동으로 조절됩니다."
        )
        description_label.setObjectName("descriptionLabel")
        description_label.setWordWrap(True)

        option_frame = QFrame()
        option_frame.setObjectName("optionFrame")

        option_layout = QHBoxLayout(option_frame)
        option_layout.setContentsMargins(14, 14, 14, 14)
        option_layout.setSpacing(10)

        self.select_all_button = QPushButton("전체 선택")
        self.clear_selection_button = QPushButton("전체 해제")
        self.select_unknown_button = QPushButton("미확인 선택")
        self.select_need_update_button = QPushButton("업데이트 필요 선택")

        self.skip_recent_checkbox = QCheckBox("최근 6시간 확인한 작가 제외")
        self.skip_recent_checkbox.setChecked(True)

        option_layout.addWidget(self.select_all_button)
        option_layout.addWidget(self.clear_selection_button)
        option_layout.addWidget(self.select_unknown_button)
        option_layout.addWidget(self.select_need_update_button)
        option_layout.addStretch()
        option_layout.addWidget(self.skip_recent_checkbox)

        self.artist_table = QTableWidget()
        self.artist_table.setColumnCount(5)
        self.artist_table.setHorizontalHeaderLabels(
            [
                "선택",
                "작가명",
                "Pixiv ID",
                "상태",
                "최근 확인",
            ]
        )
        self.artist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.artist_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.artist_table.verticalHeader().setVisible(False)
        self.artist_table.setSortingEnabled(False)
        self.artist_table.setAlternatingRowColors(True)

        artist_header = self.artist_table.horizontalHeader()

        artist_header.setStretchLastSection(False)
        artist_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents,
        )
        artist_header.setSectionResizeMode(
            1,
            QHeaderView.Stretch,
        )
        artist_header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents,
        )
        artist_header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents,
        )
        artist_header.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents,
        )

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

        self.start_button = QPushButton("시작")
        self.start_button.setObjectName("primaryButton")

        self.cancel_button = QPushButton("취소")
        self.cancel_button.setEnabled(False)

        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addWidget(self.start_button)
        progress_layout.addWidget(self.cancel_button)

        log_label = QLabel("결과 로그")
        log_label.setObjectName("sectionTitle")

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(9)
        self.log_table.setHorizontalHeaderLabels(
            [
                "시간",
                "진행",
                "결과",
                "작가명",
                "Pixiv ID",
                "로컬",
                "Pixiv",
                "누락",
                "상태",
            ]
        )
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.log_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setSortingEnabled(False)
        self.log_table.setAlternatingRowColors(True)

        log_header = self.log_table.horizontalHeader()

        log_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents,
        )
        log_header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents,
        )
        log_header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents,
        )
        log_header.setSectionResizeMode(
            3,
            QHeaderView.Stretch,
        )
        log_header.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents,
        )
        log_header.setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents,
        )
        log_header.setSectionResizeMode(
            6,
            QHeaderView.ResizeToContents,
        )
        log_header.setSectionResizeMode(
            7,
            QHeaderView.ResizeToContents,
        )
        log_header.setSectionResizeMode(
            8,
            QHeaderView.ResizeToContents,
        )

        self.status_label = QLabel("대상 작가를 선택하세요.")
        self.status_label.setObjectName("statusLabel")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(option_frame)
        layout.addWidget(self.artist_table, 2)
        layout.addLayout(progress_layout)
        layout.addWidget(log_label)
        layout.addWidget(self.log_table, 2)
        layout.addWidget(self.status_label)

        self.setStyleSheet(
            """
            QLabel#dialogTitle {
                font-size: 24px;
                font-weight: 800;
            }

            QLabel#descriptionLabel,
            QLabel#statusLabel {
                font-size: 14px;
                color: #555555;
            }

            QLabel#sectionTitle {
                font-size: 16px;
                font-weight: 700;
            }

            QFrame#optionFrame {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
            }

            QPushButton {
                padding: 8px 12px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#primaryButton {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
            }

            QPushButton#primaryButton:hover {
                background-color: #157347;
            }

            QTableWidget {
                border: 1px solid #dddddd;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #eeeeee;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #f5f5f5;
                border: none;
                border-bottom: 1px solid #dddddd;
                padding: 7px;
                font-weight: 700;
            }

            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 8px;
                text-align: center;
                height: 22px;
                background-color: #f5f5f5;
                font-size: 13px;
                font-weight: 600;
            }

            QProgressBar::chunk {
                border-radius: 8px;
                background-color: #198754;
            }
            """
        )

    def _connect_signals(self):
        self.select_all_button.clicked.connect(self._select_all)
        self.clear_selection_button.clicked.connect(self._clear_selection)
        self.select_unknown_button.clicked.connect(self._select_unknown)
        self.select_need_update_button.clicked.connect(
            self._select_need_update
        )
        self.start_button.clicked.connect(self._start_update_check)
        self.cancel_button.clicked.connect(self._cancel_update_check)

    def _load_artists(self):
        self.artist_table.setRowCount(0)
        self.artist_checkboxes = {}

        for artist in self.artists:
            row = self.artist_table.rowCount()
            self.artist_table.insertRow(row)

            checkbox = QCheckBox()
            checkbox.setChecked(False)

            self.artist_checkboxes[row] = {
                "checkbox": checkbox,
                "artist": artist,
            }

            self.artist_table.setCellWidget(row, 0, checkbox)
            self._set_table_item(row, 1, artist.get("artist_name", "-"), left=True)
            self._set_table_item(row, 2, artist.get("pixiv_id", "-"))
            self._set_table_item(row, 3, artist.get("update_status", "-"))
            self._set_table_item(
                row,
                4,
                self._format_datetime(artist.get("last_checked_at")),
            )

    def _set_table_item(self, row: int, column: int, value, left: bool = False):
        item = QTableWidgetItem(str(value))

        if left:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.artist_table.setItem(row, column, item)

    def _select_all(self):
        for item in self.artist_checkboxes.values():
            item["checkbox"].setChecked(True)

    def _clear_selection(self):
        for item in self.artist_checkboxes.values():
            item["checkbox"].setChecked(False)

    def _select_unknown(self):
        for item in self.artist_checkboxes.values():
            artist = item["artist"]
            status = str(artist.get("update_status", ""))

            item["checkbox"].setChecked(status == "unknown")

    def _select_need_update(self):
        for item in self.artist_checkboxes.values():
            artist = item["artist"]
            status = str(artist.get("update_status", ""))

            item["checkbox"].setChecked(status == "need_update")

    def _start_update_check(self):
        artist_ids = self._get_selected_artist_ids()

        if self.skip_recent_checkbox.isChecked():
            artist_ids = self._exclude_recently_checked(artist_ids)

        if not artist_ids:
            self.status_label.setText("업데이트 확인 대상이 없습니다.")
            return

        self._set_running_state(True)
        self._reset_progress(len(artist_ids))
        self.log_table.setRowCount(0)

        self.worker_thread = QThread()
        self.worker = UpdateCheckWorker(artist_ids)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.log_requested.connect(self._add_log_row)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.finished.connect(self._handle_finished)
        self.worker.failed.connect(self._handle_failed)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self._cleanup_worker)

        self.worker_thread.start()

    def _cancel_update_check(self):
        if self.worker is not None:
            self.worker.cancel()

        self.status_label.setText("취소 요청을 보냈습니다.")

    def _handle_finished(self):
        self.status_label.setText("업데이트 확인이 완료되었습니다.")
        self._set_running_state(False)
        self.update_finished.emit()

    def _handle_failed(self, message: str):
        self.status_label.setText(message)
        self._set_running_state(False)
        self.update_finished.emit()

    def _cleanup_worker(self):
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None

        if self.worker_thread is not None:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def _get_selected_artist_ids(self) -> list[int]:
        artist_ids = []

        for item in self.artist_checkboxes.values():
            if not item["checkbox"].isChecked():
                continue

            artist = item["artist"]
            artist_id = artist.get("id")

            if artist_id is None:
                continue

            artist_ids.append(int(artist_id))

        return artist_ids

    def _exclude_recently_checked(self, artist_ids: list[int]) -> list[int]:
        artist_map = {
            int(artist["id"]): artist
            for artist in self.artists
            if artist.get("id") is not None
        }

        result = []

        for artist_id in artist_ids:
            artist = artist_map.get(artist_id)

            if artist is None:
                continue

            if self._was_recently_checked(artist):
                continue

            result.append(artist_id)

        return result

    def _was_recently_checked(self, artist: dict) -> bool:
        last_checked_at = artist.get("last_checked_at")

        if not last_checked_at:
            return False

        try:
            checked_at = datetime.fromisoformat(last_checked_at)
        except ValueError:
            return False

        return datetime.now() - checked_at < timedelta(hours=6)

    def _reset_progress(self, total: int):
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"0 / {total}")
        self.status_label.setText(f"업데이트 확인 시작: {total}명")

    def _update_progress(self, current: int, total: int):
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{current} / {total}")

    def _add_log_row(self, row_data: dict):
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        values = [
            row_data.get("time", "-"),
            row_data.get("progress", "-"),
            row_data.get("result", "-"),
            row_data.get("artist_name", "-"),
            row_data.get("pixiv_id", "-"),
            row_data.get("local_count", "-"),
            row_data.get("pixiv_count", "-"),
            row_data.get("missing_count", "-"),
            row_data.get("status", "-"),
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))

            if column == 3:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            if column == 2:
                color = self.RESULT_COLORS.get(str(value))

                if color:
                    item.setBackground(QColor(color))
                    item.setForeground(QColor("white"))

            self.log_table.setItem(row, column, item)

        self.log_table.scrollToBottom()

    def _set_running_state(self, is_running: bool):
        self.start_button.setEnabled(not is_running)
        self.cancel_button.setEnabled(is_running)

        self.select_all_button.setEnabled(not is_running)
        self.clear_selection_button.setEnabled(not is_running)
        self.select_unknown_button.setEnabled(not is_running)
        self.select_need_update_button.setEnabled(not is_running)
        self.skip_recent_checkbox.setEnabled(not is_running)
        self.artist_table.setEnabled(not is_running)

    def _format_datetime(self, value) -> str:
        if value is None or value == "":
            return "-"

        try:
            dt = datetime.fromisoformat(str(value))
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return str(value)
