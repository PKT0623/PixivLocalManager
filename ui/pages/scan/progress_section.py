from PySide6.QtWidgets import (
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ScanProgressSection(QWidget):
    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.target_count_label = QLabel(
            "발견된 작가 폴더: -"
        )
        self.target_count_label.setObjectName(
            "subText"
        )

        self.current_folder_label = QLabel(
            "현재 작업: -"
        )
        self.current_folder_label.setObjectName(
            "subText"
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

        layout.addWidget(
            self.target_count_label
        )
        layout.addWidget(
            self.current_folder_label
        )
        layout.addWidget(
            self.progress_bar
        )

    def reset(self):
        self.target_count_label.setText(
            "발견된 작가 폴더: -"
        )
        self.current_folder_label.setText(
            "현재 작업: -"
        )

        self.progress_bar.setRange(
            0,
            100,
        )
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

    def update_target_count(
        self,
        total: int,
    ):
        self.target_count_label.setText(
            f"발견된 작가 폴더: {total}개"
        )

    def update_current_folder(
        self,
        folder_name: str,
    ):
        self.current_folder_label.setText(
            f"현재 작업: {folder_name}"
        )

    def update_progress(
        self,
        current: int,
        total: int,
    ):
        if total <= 0:
            self.reset()
            return

        self.progress_bar.setRange(
            0,
            total,
        )
        self.progress_bar.setValue(
            current
        )
        self.progress_bar.setFormat(
            f"{current} / {total}"
        )
