from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from .progress_parts import (
    format_extension_counts,
    format_recent_scan_history,
    format_scan_compare_info,
)


class ScanProgressSection(QWidget):
    def __init__(self):
        super().__init__()

        self.summary_labels = {}

        self._setup_ui()

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

    def reset(self):
        self.update_scan_state("대기")

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

        self.scan_start_time_label.setText("시작 시각: -")
        self.elapsed_time_label.setText("경과 시간: -")
        self.scan_speed_label.setText("진행 속도: -")
        self.estimated_time_label.setText("예상 남은 시간: -")

        self.update_summary(
            {
                "created": 0,
                "updated": 0,
                "unchanged": 0,
                "failed": 0,
            }
        )
        self.update_statistics(
            {
                "total_file_count": 0,
                "total_artwork_count": 0,
                "extension_counts": {},
                "non_artwork_file_count": 0,
                "unsupported_extension_count": 0,
                "artwork_id_not_found_count": 0,
                "empty_file_count": 0,
                "scan_error_count": 0,
            }
        )

    def reset_progress_only(self):
        self.update_scan_state("대기")
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

    def update_scan_state(
        self,
        state_text: str,
    ):
        self.scan_state_label.setText(
            f"스캔 상태: {state_text}"
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
            self.reset_progress_only()
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

    def update_runtime_info(
        self,
        info: dict,
    ):
        start_time = str(info.get("start_time_text", "-") or "-")
        elapsed_time = str(info.get("elapsed_time_text", "-") or "-")
        speed = str(info.get("speed_text", "-") or "-")
        estimated_time = str(info.get("estimated_time_text", "-") or "-")

        self.scan_start_time_label.setText(
            f"시작 시각: {start_time}"
        )
        self.elapsed_time_label.setText(
            f"경과 시간: {elapsed_time}"
        )
        self.scan_speed_label.setText(
            f"진행 속도: {speed}"
        )
        self.estimated_time_label.setText(
            f"예상 남은 시간: {estimated_time}"
        )

    def update_last_scan_info(
        self,
        info: dict | None,
    ):
        if not info:
            self.last_scan_time_label.setText("마지막 스캔: -")
            return

        finished_at = str(info.get("finished_at_text", "") or "")
        total = int(info.get("total", 0) or 0)
        created = int(info.get("created", 0) or 0)
        updated = int(info.get("updated", 0) or 0)
        failed = int(info.get("failed", 0) or 0)
        non_artwork_file_count = int(
            info.get("non_artwork_file_count", 0) or 0
        )

        if not finished_at:
            self.last_scan_time_label.setText("마지막 스캔: -")
            return

        self.last_scan_time_label.setText(
            "마지막 스캔: "
            f"{finished_at} / 대상 {total}개 / "
            f"등록 {created}, 업데이트 {updated}, 실패 {failed}, "
            f"비작품 {non_artwork_file_count}"
        )

    def update_recent_scan_history(
        self,
        history: list[dict],
    ):
        self.recent_scan_history_label.setText(
            format_recent_scan_history(history)
        )

    def update_scan_compare_info(
        self,
        compare_result: dict | None,
    ):
        self.scan_compare_label.setText(
            format_scan_compare_info(compare_result)
        )

    def update_statistics(
        self,
        statistics: dict,
    ):
        total_file_count = int(
            statistics.get("total_file_count", 0) or 0
        )
        total_artwork_count = int(
            statistics.get("total_artwork_count", 0) or 0
        )
        extension_counts = statistics.get("extension_counts", {}) or {}
        non_artwork_file_count = int(
            statistics.get("non_artwork_file_count", 0) or 0
        )

        self.total_file_count_label.setText(
            f"총 파일 수: {total_file_count}"
        )
        self.total_artwork_count_label.setText(
            f"총 작품 수: {total_artwork_count}"
        )
        self.non_artwork_file_count_label.setText(
            f"비작품 파일 수: {non_artwork_file_count}"
        )
        self.non_artwork_summary_label.setText(
            "비작품 파일 요약: "
            f"{self._format_non_artwork_summary(statistics)}"
        )
        self.extension_counts_label.setText(
            "확장자별 파일 수: "
            f"{format_extension_counts(extension_counts)}"
        )

    def _format_non_artwork_summary(
        self,
        statistics: dict,
    ) -> str:
        items = []

        summary_fields = [
            ("unsupported_extension_count", "지원하지 않는 확장자"),
            ("artwork_id_not_found_count", "작품 ID 추출 실패"),
            ("empty_file_count", "0바이트"),
            ("scan_error_count", "파일 확인 오류"),
        ]

        for key, label in summary_fields:
            count = int(statistics.get(key, 0) or 0)

            if count <= 0:
                continue

            items.append(f"{label} {count}개")

        if not items:
            return "-"

        return " / ".join(items)
