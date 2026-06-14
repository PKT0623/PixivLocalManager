from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from .actions import UpdateCheckActions
from .artist_table import UpdateArtistTable
from .log_table import UpdateLogTable
from .selection_actions import UpdateSelectionActions


class UpdateCheckDialog(QDialog):
    update_finished = Signal()

    def __init__(self, artists: list[dict], parent=None):
        super().__init__(parent)

        self.artists = artists
        self.worker_thread = None
        self.worker = None

        self.actions = UpdateCheckActions(self)
        self.selection_actions = UpdateSelectionActions(self)

        self.setWindowTitle("Pixiv 업데이트 확인")
        self.resize(980, 720)

        self._setup_ui()
        self._connect_signals()
        self.artist_table.load_artists(self.artists)

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

        self.artist_table = UpdateArtistTable()

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

        self.log_table = UpdateLogTable()

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
        self.select_all_button.clicked.connect(
            self.selection_actions.select_all
        )
        self.clear_selection_button.clicked.connect(
            self.selection_actions.clear_selection
        )
        self.select_unknown_button.clicked.connect(
            self.selection_actions.select_unknown
        )
        self.select_need_update_button.clicked.connect(
            self.selection_actions.select_need_update
        )
        self.start_button.clicked.connect(
            self.actions.start_update_check
        )
        self.cancel_button.clicked.connect(
            self.actions.cancel_update_check
        )
