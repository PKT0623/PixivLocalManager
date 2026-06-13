from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.artist_service import ArtistService
from app.services.settings_service import SettingsService


class ScanWorker(QObject):
    log_message_requested = Signal(str)
    scan_result_requested = Signal(dict)
    progress_updated = Signal(int, int)
    current_folder_changed = Signal(str)
    target_count_changed = Signal(int)
    finished = Signal()
    failed = Signal(str)

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    def __init__(self, root_folder_path: str):
        super().__init__()

        self.root_folder_path = root_folder_path
        self.artist_service = ArtistService()

    def run(self):
        try:
            root_folder = Path(self.root_folder_path)

            if not root_folder.exists() or not root_folder.is_dir():
                raise ValueError("선택한 폴더가 존재하지 않습니다.")

            self.log_message_requested.emit("작가 폴더 탐색을 시작합니다.")
            artist_folders = self._find_artist_folders(root_folder)

            self.target_count_changed.emit(len(artist_folders))
            self.progress_updated.emit(0, len(artist_folders))

            if not artist_folders:
                self.log_message_requested.emit(
                    "이미지 파일이 있는 작가 폴더를 찾지 못했습니다."
                )
                self.finished.emit()
                return

            self.log_message_requested.emit(
                f"발견된 작가 폴더: {len(artist_folders)}개"
            )

            created_count = 0
            updated_count = 0
            fail_count = 0

            for index, folder_path in enumerate(artist_folders, start=1):
                self.current_folder_changed.emit(folder_path.name)

                try:
                    result = self._scan_artist_folder(folder_path)
                    action = result.get("action")
                    artist = result.get("artist") or {}

                    if action == "created":
                        created_count += 1
                        result_label = "등록"
                    else:
                        updated_count += 1
                        result_label = "업데이트"

                    self.scan_result_requested.emit(
                        self._build_scan_result_row(
                            index=index,
                            total=len(artist_folders),
                            result=result_label,
                            artist=artist,
                        )
                    )
                except Exception as error:
                    fail_count += 1
                    self.scan_result_requested.emit(
                        {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "progress": f"{index}/{len(artist_folders)}",
                            "result": "실패",
                            "artist_name": folder_path.name,
                            "pixiv_id": "-",
                            "artwork_count": "-",
                            "file_count": "-",
                            "update_status": str(error),
                        }
                    )

                self.progress_updated.emit(index, len(artist_folders))

            self.current_folder_changed.emit("-")
            self.log_message_requested.emit(
                "전체 스캔 완료: "
                f"등록 {created_count}개, "
                f"업데이트 {updated_count}개, "
                f"실패 {fail_count}개"
            )
        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit()

    def _find_artist_folders(self, root_folder: Path) -> list[Path]:
        artist_folders = []

        for folder_path in self._iter_folders(root_folder, max_depth=3):
            if self._has_image_files(folder_path):
                artist_folders.append(folder_path)

        artist_folders = sorted(
            set(artist_folders),
            key=lambda path: str(path).lower(),
        )

        return artist_folders

    def _iter_folders(self, root_folder: Path, max_depth: int) -> list[Path]:
        folders = []

        def walk(current_folder: Path, depth: int):
            if depth > max_depth:
                return

            try:
                child_folders = [
                    path
                    for path in current_folder.iterdir()
                    if path.is_dir()
                ]
            except OSError:
                return

            for child_folder in child_folders:
                folders.append(child_folder)
                walk(child_folder, depth + 1)

        walk(root_folder, 1)

        if self._has_image_files(root_folder):
            folders.insert(0, root_folder)

        return folders

    def _has_image_files(self, folder_path: Path) -> bool:
        try:
            for file_path in folder_path.iterdir():
                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() in self.IMAGE_EXTENSIONS:
                    return True
        except OSError:
            return False

        return False

    def _scan_artist_folder(self, folder_path: Path) -> dict:
        return self.artist_service.save_scanned_artist(
            str(folder_path)
        )

    def _build_scan_result_row(
        self,
        index: int,
        total: int,
        result: str,
        artist: dict,
    ) -> dict:
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": f"{index}/{total}",
            "result": result,
            "artist_name": str(artist.get("artist_name", "") or "-"),
            "pixiv_id": str(artist.get("pixiv_id", "") or "-"),
            "artwork_count": str(artist.get("folder_artwork_count", 0)),
            "file_count": str(artist.get("folder_file_count", 0)),
            "update_status": str(artist.get("update_status", "") or "-"),
        }


class ScanPage(QWidget):
    RESULT_COLORS = {
        "등록": "#198754",
        "업데이트": "#0d6efd",
        "실패": "#dc3545",
        "정보": "#6c757d",
    }

    STATUS_COLORS = {
        "unknown": "#6c757d",
        "latest": "#198754",
        "up_to_date": "#198754",
        "need_update": "#fd7e14",
        "updated": "#0d6efd",
        "error": "#dc3545",
    }

    def __init__(self):
        super().__init__()

        self.scan_thread = None
        self.scan_worker = None
        self.settings_service = SettingsService()

        self._setup_ui()
        self._connect_signals()
        self._load_default_folder()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title_label = QLabel("폴더 스캔")
        title_label.setObjectName("pageTitle")

        description_label = QLabel(
            "Pixiv 이미지 폴더를 선택하고 최대 3단계 하위 폴더까지 분석해 DB에 등록합니다."
        )
        description_label.setObjectName("pageDescription")

        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")

        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setSpacing(12)

        folder_label = QLabel("스캔할 폴더")
        folder_label.setObjectName("sectionTitle")

        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(8)

        self.folder_path_input = QLineEdit()
        self.folder_path_input.setReadOnly(True)
        self.folder_path_input.setPlaceholderText("폴더를 선택하세요.")

        self.folder_select_button = QPushButton("폴더 선택")
        self.folder_select_button.setObjectName("folderSelectButton")

        self.scan_button = QPushButton("스캔 및 등록")
        self.scan_button.setObjectName("scanButton")

        folder_layout.addWidget(self.folder_path_input, 1)
        folder_layout.addWidget(self.folder_select_button)
        folder_layout.addWidget(self.scan_button)

        self.target_count_label = QLabel("발견된 작가 폴더: -")
        self.target_count_label.setObjectName("subText")

        self.current_folder_label = QLabel("현재 작업: -")
        self.current_folder_label.setObjectName("subText")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

        input_layout.addWidget(folder_label)
        input_layout.addLayout(folder_layout)
        input_layout.addWidget(self.target_count_label)
        input_layout.addWidget(self.current_folder_label)
        input_layout.addWidget(self.progress_bar)

        log_header_layout = QHBoxLayout()

        log_label = QLabel("결과 로그")
        log_label.setObjectName("sectionTitle")

        self.clear_log_button = QPushButton("로그 지우기")
        self.clear_log_button.setObjectName("clearLogButton")

        log_header_layout.addWidget(log_label)
        log_header_layout.addStretch()
        log_header_layout.addWidget(self.clear_log_button)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(8)
        self.log_table.setHorizontalHeaderLabels(
            [
                "시간",
                "진행",
                "결과",
                "작가명",
                "Pixiv ID",
                "작품 수",
                "파일 수",
                "상태",
            ]
        )
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.log_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.log_table.setSortingEnabled(False)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setShowGrid(True)

        header = self.log_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        self.log_table.verticalHeader().setDefaultSectionSize(30)

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(input_frame)
        layout.addLayout(log_header_layout)
        layout.addWidget(self.log_table, 1)

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

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#subText {
                font-size: 14px;
                color: #555555;
            }

            QFrame#inputFrame {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
            }

            QLineEdit {
                border: 1px solid #dddddd;
                border-radius: 6px;
                padding: 8px 10px;
                background-color: #f9f9f9;
                font-size: 14px;
            }

            QPushButton {
                padding: 8px 14px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#scanButton {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
                min-width: 110px;
            }

            QPushButton#scanButton:hover {
                background-color: #157347;
            }

            QPushButton#folderSelectButton,
            QPushButton#clearLogButton {
                min-width: 100px;
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

            QTableWidget {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
                gridline-color: #eeeeee;
                font-size: 13px;
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

    def _connect_signals(self):
        self.folder_select_button.clicked.connect(self._select_folder)
        self.scan_button.clicked.connect(self._start_scan)
        self.clear_log_button.clicked.connect(self._clear_log)

    def _load_default_folder(self):
        folder_path = self.settings_service.get_setting(
            "pixiv_root_folder"
        )

        if not folder_path:
            return

        self.folder_path_input.setText(folder_path)
        self._add_info_log(f"기본 Pixiv 폴더 불러옴: {folder_path}")

    def _select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "스캔할 폴더 선택",
            self.folder_path_input.text().strip(),
        )

        if not folder_path:
            return

        self.folder_path_input.setText(folder_path)
        self._add_info_log(f"폴더 선택: {folder_path}")

    def _start_scan(self):
        folder_path = self.folder_path_input.text().strip()

        if not folder_path:
            self._add_info_log("오류: 먼저 폴더를 선택하세요.")
            return

        if self.scan_thread is not None:
            self._add_info_log("이미 스캔이 진행 중입니다.")
            return

        self._set_scanning_state(True)
        self._reset_progress()

        self._add_info_log("스캔 작업을 시작합니다.")
        self._add_info_log(f"대상 폴더: {folder_path}")
        self._add_info_log("탐색 깊이: 최대 3단계")

        self.scan_thread = QThread()
        self.scan_worker = ScanWorker(folder_path)
        self.scan_worker.moveToThread(self.scan_thread)

        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.log_message_requested.connect(self._add_info_log)
        self.scan_worker.scan_result_requested.connect(
            self._add_scan_result_log
        )
        self.scan_worker.progress_updated.connect(self._update_progress)
        self.scan_worker.current_folder_changed.connect(
            self._update_current_folder
        )
        self.scan_worker.target_count_changed.connect(
            self._update_target_count
        )
        self.scan_worker.failed.connect(self._handle_scan_failed)
        self.scan_worker.finished.connect(self._handle_scan_finished)

        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.failed.connect(self.scan_thread.quit)
        self.scan_thread.finished.connect(self._cleanup_scan_thread)

        self.scan_thread.start()

    def _handle_scan_finished(self):
        self._add_info_log("스캔 작업이 완료되었습니다.")
        self._set_scanning_state(False)

    def _handle_scan_failed(self, error_message: str):
        self._add_scan_result_log(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": "-",
                "result": "실패",
                "artist_name": error_message,
                "pixiv_id": "-",
                "artwork_count": "-",
                "file_count": "-",
                "update_status": "error",
            }
        )
        self._set_scanning_state(False)

    def _cleanup_scan_thread(self):
        if self.scan_worker is not None:
            self.scan_worker.deleteLater()
            self.scan_worker = None

        if self.scan_thread is not None:
            self.scan_thread.deleteLater()
            self.scan_thread = None

    def _set_scanning_state(self, is_scanning: bool):
        self.scan_button.setEnabled(not is_scanning)
        self.folder_select_button.setEnabled(not is_scanning)

        if is_scanning:
            self.scan_button.setText("스캔 중...")
        else:
            self.scan_button.setText("스캔 및 등록")

    def _reset_progress(self):
        self.target_count_label.setText("발견된 작가 폴더: -")
        self.current_folder_label.setText("현재 작업: -")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

    def _update_target_count(self, total: int):
        self.target_count_label.setText(f"발견된 작가 폴더: {total}개")

    def _update_current_folder(self, folder_name: str):
        self.current_folder_label.setText(f"현재 작업: {folder_name}")

    def _update_progress(self, current: int, total: int):
        if total <= 0:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0 / 0")
            return

        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{current} / {total}")

    def _add_info_log(self, message: str):
        self._add_log_row(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": "-",
                "result": "정보",
                "artist_name": message,
                "pixiv_id": "-",
                "artwork_count": "-",
                "file_count": "-",
                "update_status": "-",
            }
        )

    def _add_scan_result_log(self, row_data: dict):
        self._add_log_row(row_data)

    def _add_log_row(self, row_data: dict):
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        values = [
            row_data.get("time", "-"),
            row_data.get("progress", "-"),
            row_data.get("result", "-"),
            row_data.get("artist_name", "-"),
            row_data.get("pixiv_id", "-"),
            row_data.get("artwork_count", "-"),
            row_data.get("file_count", "-"),
            row_data.get("update_status", "-"),
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            self._apply_item_alignment(item, column)
            self._apply_item_color(item, column, values)
            self.log_table.setItem(row, column, item)

        self.log_table.scrollToBottom()

    def _apply_item_alignment(
        self,
        item: QTableWidgetItem,
        column: int,
    ):
        if column in (0, 1, 2, 4, 5, 6, 7):
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def _apply_item_color(
        self,
        item: QTableWidgetItem,
        column: int,
        values: list,
    ):
        result = values[2]
        status = values[7]

        if column == 2:
            color = self.RESULT_COLORS.get(result)

            if color is not None:
                item.setForeground(QColor("#ffffff"))
                item.setBackground(QColor(color))

        if column == 7:
            color = self.STATUS_COLORS.get(status)

            if color is not None:
                item.setForeground(QColor("#ffffff"))
                item.setBackground(QColor(color))

    def _clear_log(self):
        self.log_table.setRowCount(0)
