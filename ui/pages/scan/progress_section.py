from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ScanProgressSection(QWidget):
    def __init__(self):
        super().__init__()

        self.summary_labels = {}

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

        summary_layout = QGridLayout()
        summary_layout.setContentsMargins(0, 4, 0, 0)
        summary_layout.setHorizontalSpacing(12)
        summary_layout.setVerticalSpacing(6)

        self._add_summary_label(summary_layout, "created", "신규 등록", 0, 0)
        self._add_summary_label(summary_layout, "updated", "업데이트", 0, 1)
        self._add_summary_label(summary_layout, "unchanged", "변경 없음", 0, 2)
        self._add_summary_label(summary_layout, "failed", "실패", 0, 3)

        layout.addWidget(
            self.target_count_label
        )
        layout.addWidget(
            self.current_folder_label
        )
        layout.addWidget(
            self.progress_bar
        )
        layout.addLayout(summary_layout)

    def _add_summary_label(
        self,
        layout: QGridLayout,
        key: str,
        title: str,
        row: int,
        column: int,
    ):
        label = QLabel(f"{title}: 0")
        label.setObjectName("subText")

        self.summary_labels[key] = {
            "label": label,
            "title": title,
        }

        layout.addWidget(label, row, column)

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

        self.update_summary(
            {
                "created": 0,
                "updated": 0,
                "unchanged": 0,
                "failed": 0,
            }
        )

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

    def update_summary(
        self,
        summary: dict,
    ):
        for key, item in self.summary_labels.items():
            label = item["label"]
            title = item["title"]
            count = int(summary.get(key, 0) or 0)

            label.setText(f"{title}: {count}")
