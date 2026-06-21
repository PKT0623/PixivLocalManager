from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..log_table import UpdateLogTable


class UpdateCheckLogFrameMixin:
    def _create_log_frame(self) -> QFrame:
        log_frame = QFrame()
        log_frame.setObjectName("logFrame")

        frame_layout = QVBoxLayout(log_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_label = QLabel("결과 로그")
        title_label.setObjectName("sectionTitle")

        self.log_table = UpdateLogTable()

        frame_layout.addWidget(title_label)
        frame_layout.addWidget(self.log_table, 1)

        return log_frame
