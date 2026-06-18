from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .actions import PixivManagerActions
from .bookmark_table import BookmarkArtworkTable
from .follow_table import FollowUserTable
from .log_table import PixivManagerLogTable
from .styles import PIXIV_MANAGER_PAGE_STYLES
from .summary_section import PixivManagerSummarySection


class PixivManagerPage(QWidget):
    def __init__(self):
        super().__init__()

        self.worker_thread = None
        self.worker = None

        self.actions = PixivManagerActions(self)

        self._setup_ui()
        self._connect_signals()
        self.actions.load_saved_page_size()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_label = QLabel("Pixiv 관리")
        title_label.setObjectName("pageTitle")

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.setObjectName("primaryButton")

        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(self.refresh_button)

        self.import_frame = self._create_import_frame()
        self.summary_section = PixivManagerSummarySection()
        self.table_frame = self._create_table_frame()
        self.log_frame = self._create_log_frame()

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")

        layout.addLayout(header_layout)
        layout.addWidget(self.import_frame)
        layout.addWidget(self.summary_section)
        layout.addWidget(self.table_frame, 4)
        layout.addWidget(self.log_frame, 2)
        layout.addWidget(self.status_label)

        self.setStyleSheet(PIXIV_MANAGER_PAGE_STYLES)

    def _create_import_frame(self) -> QFrame:
        import_frame = QFrame()
        import_frame.setObjectName("importFrame")

        frame_layout = QVBoxLayout(import_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_label = QLabel("가져오기")
        title_label.setObjectName("sectionTitle")

        path_layout = QHBoxLayout()
        path_layout.setSpacing(8)

        path_label = QLabel("파일 경로")

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText(
            "예: test_follow_ids.txt 또는 C:\\\\path\\\\ids.csv"
        )

        self.browse_file_button = QPushButton("찾아보기")

        path_layout.addWidget(path_label)
        path_layout.addWidget(self.file_path_input, 1)
        path_layout.addWidget(self.browse_file_button)

        option_layout = QHBoxLayout()
        option_layout.setSpacing(10)

        self.import_target_combo = QComboBox()
        self.import_target_combo.addItems(
            [
                "팔로우 유저",
                "북마크 작품",
            ]
        )

        self.import_file_type_combo = QComboBox()
        self.import_file_type_combo.addItems(
            [
                "자동 감지",
                "TXT",
                "CSV",
            ]
        )

        self.import_file_button = QPushButton("가져오기")
        self.import_file_button.setObjectName("primaryButton")

        self.cancel_import_button = QPushButton("취소")
        self.cancel_import_button.setEnabled(False)

        self.clear_log_button = QPushButton("로그 초기화")

        self.pixiv_follow_button = QPushButton("Pixiv 팔로우 가져오기")
        self.pixiv_bookmark_button = QPushButton("Pixiv 북마크 가져오기")

        option_layout.addWidget(QLabel("등록 대상"))
        option_layout.addWidget(self.import_target_combo)
        option_layout.addWidget(QLabel("파일 형식"))
        option_layout.addWidget(self.import_file_type_combo)
        option_layout.addWidget(self.import_file_button)
        option_layout.addWidget(self.cancel_import_button)
        option_layout.addStretch()
        option_layout.addWidget(self.pixiv_follow_button)
        option_layout.addWidget(self.pixiv_bookmark_button)
        option_layout.addWidget(self.clear_log_button)

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

        self.estimated_time_label = QLabel("예상 남은 시간: -")
        self.estimated_time_label.setObjectName("statusLabel")

        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addWidget(self.estimated_time_label)

        frame_layout.addWidget(title_label)
        frame_layout.addLayout(path_layout)
        frame_layout.addLayout(option_layout)
        frame_layout.addLayout(progress_layout)

        return import_frame

    def _create_table_frame(self) -> QFrame:
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")

        frame_layout = QVBoxLayout(table_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        title_label = QLabel("목록")
        title_label.setObjectName("sectionTitle")

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            [
                "전체",
                "등록",
                "동기화 필요",
                "완료",
                "대기",
                "실패",
                "스킵",
            ]
        )

        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(
            [
                "100",
                "300",
                "500",
                "1000",
            ]
        )

        self.prev_page_button = QPushButton("이전")
        self.next_page_button = QPushButton("다음")
        self.page_info_label = QLabel("페이지: 0 / 0")
        self.page_info_label.setObjectName("statusLabel")

        self.display_count_label = QLabel("표시: 0 / 0")
        self.display_count_label.setObjectName("statusLabel")

        self.select_all_button = QPushButton("전체 선택")
        self.clear_selection_button = QPushButton("선택 해제")
        self.open_selected_button = QPushButton("선택 Pixiv 열기")
        self.delete_selected_button = QPushButton("선택 삭제")
        self.delete_displayed_button = QPushButton("현재 페이지 삭제")

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(QLabel("필터"))
        title_layout.addWidget(self.filter_combo)
        title_layout.addWidget(QLabel("페이지 크기"))
        title_layout.addWidget(self.page_size_combo)
        title_layout.addWidget(self.prev_page_button)
        title_layout.addWidget(self.page_info_label)
        title_layout.addWidget(self.next_page_button)
        title_layout.addWidget(self.display_count_label)
        title_layout.addWidget(self.select_all_button)
        title_layout.addWidget(self.clear_selection_button)
        title_layout.addWidget(self.open_selected_button)
        title_layout.addWidget(self.delete_selected_button)
        title_layout.addWidget(self.delete_displayed_button)

        self.tab_widget = QTabWidget()

        self.follow_table = FollowUserTable()
        self.bookmark_table = BookmarkArtworkTable()

        self.tab_widget.addTab(self.follow_table, "팔로우 유저")
        self.tab_widget.addTab(self.bookmark_table, "북마크 작품")

        frame_layout.addLayout(title_layout)
        frame_layout.addWidget(self.tab_widget, 1)

        return table_frame

    def _create_log_frame(self) -> QFrame:
        log_frame = QFrame()
        log_frame.setObjectName("logFrame")

        frame_layout = QVBoxLayout(log_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_label = QLabel("결과 로그")
        title_label.setObjectName("sectionTitle")

        self.log_table = PixivManagerLogTable()

        frame_layout.addWidget(title_label)
        frame_layout.addWidget(self.log_table, 1)

        return log_frame

    def _connect_signals(self):
        self.refresh_button.clicked.connect(self.actions.load_data)
        self.browse_file_button.clicked.connect(self.actions.browse_file)
        self.import_file_button.clicked.connect(self.actions.import_file)
        self.cancel_import_button.clicked.connect(self.actions.cancel_import)
        self.clear_log_button.clicked.connect(self.actions.clear_logs)

        self.pixiv_follow_button.clicked.connect(
            self.actions.import_pixiv_follow
        )
        self.pixiv_bookmark_button.clicked.connect(
            self.actions.import_pixiv_bookmark
        )

        self.filter_combo.currentIndexChanged.connect(
            self.actions.reset_page_and_apply_filters
        )
        self.page_size_combo.currentIndexChanged.connect(
            self.actions.handle_page_size_changed
        )
        self.prev_page_button.clicked.connect(self.actions.prev_page)
        self.next_page_button.clicked.connect(self.actions.next_page)

        self.tab_widget.currentChanged.connect(
            self.actions.handle_tab_changed
        )
        self.select_all_button.clicked.connect(
            self.actions.select_all_displayed
        )
        self.clear_selection_button.clicked.connect(
            self.actions.clear_selection
        )
        self.open_selected_button.clicked.connect(
            self.actions.open_selected_pixiv
        )
        self.delete_selected_button.clicked.connect(
            self.actions.delete_selected
        )
        self.delete_displayed_button.clicked.connect(
            self.actions.delete_displayed
        )

    def load_data(self):
        self.actions.load_data()

    def shutdown_worker(self):
        self.actions.shutdown_worker()
