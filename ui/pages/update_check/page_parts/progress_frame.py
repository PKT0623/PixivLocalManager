from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)


class UpdateCheckProgressFrameMixin:
    def _create_progress_frame(self) -> QFrame:
        progress_frame = QFrame()
        progress_frame.setObjectName("progressFrame")

        frame_layout = QVBoxLayout(progress_frame)
        frame_layout.setContentsMargins(14, 12, 14, 12)
        frame_layout.setSpacing(8)

        title_label = QLabel("실행")
        title_label.setObjectName("sectionTitle")

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

        self.start_button = QPushButton("시작")
        self.start_button.setObjectName("primaryButton")

        self.pause_button = QPushButton("일시정지")
        self.pause_button.setEnabled(False)

        self.resume_button = QPushButton("재개")
        self.resume_button.setEnabled(False)

        self.cancel_button = QPushButton("중지")
        self.cancel_button.setEnabled(False)

        self.export_csv_button = QPushButton("CSV 저장")
        self.export_csv_button.setEnabled(False)

        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addWidget(self.start_button)
        progress_layout.addWidget(self.pause_button)
        progress_layout.addWidget(self.resume_button)
        progress_layout.addWidget(self.cancel_button)
        progress_layout.addWidget(self.export_csv_button)

        frame_layout.addWidget(title_label)
        frame_layout.addLayout(progress_layout)

        return progress_frame
