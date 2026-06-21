from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ..log_table import UpdateLogTable


class UpdateCheckLogFrameMixin:
    def _create_log_frame(self) -> QFrame:
        log_frame = QFrame()
        log_frame.setObjectName("logFrame")

        frame_layout = QVBoxLayout(log_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_label = QLabel("결과 로그")
        title_label.setObjectName("sectionTitle")

        self.open_log_artist_detail_button = QPushButton("상세 열기")
        self.open_log_artist_list_button = QPushButton("목록에서 보기")
        self.rescan_selected_log_button = QPushButton("선택 재스캔")
        self.rescan_missing_log_button = QPushButton("누락 재스캔")
        self.rescan_error_log_button = QPushButton("오류 재스캔")
        self.export_download_txt_button = QPushButton("다운로드 TXT")
        self.export_download_csv_button = QPushButton("다운로드 CSV")
        self.export_csv_button = QPushButton("결과 CSV")

        buttons = (
            self.open_log_artist_detail_button,
            self.open_log_artist_list_button,
            self.rescan_selected_log_button,
            self.rescan_missing_log_button,
            self.rescan_error_log_button,
            self.export_download_txt_button,
            self.export_download_csv_button,
            self.export_csv_button,
        )

        for button in buttons:
            button.setEnabled(False)

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        for button in buttons:
            header_layout.addWidget(button)

        self.log_table = UpdateLogTable()

        frame_layout.addLayout(header_layout)
        frame_layout.addWidget(self.log_table, 1)

        return log_frame
