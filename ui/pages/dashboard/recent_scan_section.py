from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .utils import format_datetime


class RecentScanSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
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

    def update_recent_scan_time(self, artists: list[dict]):
        scan_times = [
            str(artist.get("last_checked_at", "") or "")
            for artist in artists
            if artist.get("last_checked_at")
        ]

        if not scan_times:
            self.recent_scan_label.setText("-")
            return

        self.recent_scan_label.setText(format_datetime(max(scan_times)))
