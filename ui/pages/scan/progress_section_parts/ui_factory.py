from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
)


class ScanProgressUiFactoryMixin:
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.scan_state_label = QLabel(
            "스캔 상태: 대기"
        )
        self.scan_state_label.setObjectName(
            "subText"
        )

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

        info_frame = self._create_info_frame()
        statistics_frame = self._create_statistics_frame()
        history_frame = self._create_history_frame()

        layout.addWidget(
            self.scan_state_label
        )
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
        layout.addWidget(info_frame)
        layout.addWidget(statistics_frame)
        layout.addWidget(history_frame)

    def _create_info_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("scanSubFrame")

        layout = QGridLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(6)

        self.scan_start_time_label = self._create_sub_text(
            "시작 시각: -"
        )
        self.elapsed_time_label = self._create_sub_text(
            "경과 시간: -"
        )
        self.scan_speed_label = self._create_sub_text(
            "진행 속도: -"
        )
        self.estimated_time_label = self._create_sub_text(
            "예상 남은 시간: -"
        )
        self.last_scan_time_label = self._create_sub_text(
            "마지막 스캔: -"
        )

        layout.addWidget(self.scan_start_time_label, 0, 0)
        layout.addWidget(self.elapsed_time_label, 0, 1)
        layout.addWidget(self.scan_speed_label, 0, 2)
        layout.addWidget(self.estimated_time_label, 1, 0)
        layout.addWidget(self.last_scan_time_label, 1, 1, 1, 2)

        return frame

    def _create_statistics_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("scanSubFrame")

        layout = QGridLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(6)

        self.total_file_count_label = self._create_sub_text(
            "총 파일 수: 0"
        )
        self.total_artwork_count_label = self._create_sub_text(
            "총 작품 수: 0"
        )
        self.non_artwork_file_count_label = self._create_sub_text(
            "비작품 파일 수: 0"
        )
        self.non_artwork_summary_label = self._create_sub_text(
            "비작품 파일 요약: -"
        )
        self.extension_counts_label = self._create_sub_text(
            "확장자별 파일 수: -"
        )

        layout.addWidget(self.total_file_count_label, 0, 0)
        layout.addWidget(self.total_artwork_count_label, 0, 1)
        layout.addWidget(self.non_artwork_file_count_label, 0, 2)
        layout.addWidget(self.non_artwork_summary_label, 1, 0, 1, 3)
        layout.addWidget(self.extension_counts_label, 2, 0, 1, 3)

        return frame

    def _create_history_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("scanSubFrame")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        history_title = QLabel("최근 스캔 목록")
        history_title.setObjectName("subSectionTitle")

        self.recent_scan_history_label = self._create_sub_text(
            "최근 스캔 기록이 없습니다."
        )
        self.recent_scan_history_label.setWordWrap(True)

        compare_title = QLabel("직전 스캔 대비")
        compare_title.setObjectName("subSectionTitle")

        self.scan_compare_label = self._create_sub_text(
            "비교할 이전 스캔 기록이 없습니다."
        )
        self.scan_compare_label.setWordWrap(True)

        layout.addWidget(history_title)
        layout.addWidget(self.recent_scan_history_label)
        layout.addWidget(compare_title)
        layout.addWidget(self.scan_compare_label)

        return frame

    def _create_sub_text(
        self,
        text: str,
    ) -> QLabel:
        label = QLabel(text)
        label.setObjectName("subText")
        return label

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
