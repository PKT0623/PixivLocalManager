from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
)

from .recent_activity_parts import (
    RecentActivityRowUtilsMixin,
    RecentActivityTableFactoryMixin,
    RecentActivityTableUpdatersMixin,
)


class RecentActivitySection(
    QFrame,
    RecentActivityTableFactoryMixin,
    RecentActivityTableUpdatersMixin,
    RecentActivityRowUtilsMixin,
):
    artist_detail_requested = Signal(int)

    ACTIVITY_TABS = [
        ("recent_viewed_artists", "최근 열람"),
        ("recent_registered_artists", "최근 등록"),
        ("recent_checked_artists", "최근 확인"),
        ("recent_update_histories", "업데이트 이력"),
        ("recent_error_histories", "오류 작가"),
        ("missing_increased_histories", "누락 증가"),
    ]

    def __init__(self):
        super().__init__()

        self.current_data = {}
        self.tab_buttons = {}
        self.tables = {}

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_label = QLabel("최근 활동")
        title_label.setObjectName("sectionTitle")

        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(5)

        for index, (key, title) in enumerate(self.ACTIVITY_TABS):
            button = QPushButton(title)
            button.setObjectName("limitButton")
            button.clicked.connect(
                lambda checked=False, value=index: self.set_active_tab(value)
            )

            self.tab_buttons[index] = button
            tab_layout.addWidget(button)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(tab_layout)

        self.stack = QStackedWidget()
        self._setup_activity_tables()

        layout.addLayout(header_layout)
        layout.addWidget(self.stack, 1)

        self.set_active_tab(0)

    def set_active_tab(self, index: int):
        self.stack.setCurrentIndex(index)

        for tab_index, button in self.tab_buttons.items():
            is_active = tab_index == index
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def update_recent_activity(self, data: dict):
        self.current_data = data

        self._update_artist_table("recent_viewed_artists")
        self._update_artist_table("recent_registered_artists")
        self._update_artist_table("recent_checked_artists")
        self._update_update_history_table()
        self._update_error_history_table()
        self._update_missing_increased_table()
