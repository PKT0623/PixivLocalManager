from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton


class ScanPreviewHeaderMixin:
    def _setup_preview_header(self):
        self.preview_header_layout = QHBoxLayout()

        preview_label = QLabel("스캔 미리보기")
        preview_label.setObjectName("sectionTitle")

        self.preview_summary_label = QLabel(
            "신규 0 / 업데이트 0 / 변경 없음 0 / 오류 0 / 선택 0"
        )
        self.preview_summary_label.setObjectName("subText")

        self.preview_show_created_checkbox = QCheckBox("신규만 보기")
        self.preview_show_updated_checkbox = QCheckBox("업데이트만 보기")
        self.preview_show_error_checkbox = QCheckBox("오류만 보기")

        self.preview_hide_unchanged_checkbox = QCheckBox("변경 없음 숨김")
        self.preview_hide_unchanged_checkbox.setChecked(False)

        self.preview_select_all_button = QPushButton("전체 선택")
        self.preview_clear_selection_button = QPushButton("전체 해제")
        self.preview_exclude_selected_button = QPushButton("선택 제외")
        self.preview_keep_selected_button = QPushButton("선택만 남김")
        self.preview_exclude_error_button = QPushButton("오류 제외")
        self.preview_export_csv_button = QPushButton("미리보기 CSV")
        self.preview_export_non_artwork_txt_button = QPushButton(
            "비작품 TXT"
        )
        self.preview_export_non_artwork_csv_button = QPushButton(
            "비작품 CSV"
        )
        self.preview_scan_selected_button = QPushButton("선택 항목 등록")

        self._setup_preview_button_styles()
        self._add_preview_header_widgets(preview_label)

    def _setup_preview_button_styles(self):
        clear_buttons = (
            self.preview_select_all_button,
            self.preview_clear_selection_button,
            self.preview_exclude_selected_button,
            self.preview_keep_selected_button,
            self.preview_exclude_error_button,
            self.preview_export_csv_button,
            self.preview_export_non_artwork_txt_button,
            self.preview_export_non_artwork_csv_button,
        )

        for button in clear_buttons:
            button.setObjectName("clearLogButton")

        self.preview_scan_selected_button.setObjectName("scanButton")

    def _add_preview_header_widgets(
        self,
        preview_label: QLabel,
    ):
        self.preview_header_layout.addWidget(preview_label)
        self.preview_header_layout.addWidget(self.preview_summary_label)
        self.preview_header_layout.addStretch()
        self.preview_header_layout.addWidget(
            self.preview_show_created_checkbox
        )
        self.preview_header_layout.addWidget(
            self.preview_show_updated_checkbox
        )
        self.preview_header_layout.addWidget(
            self.preview_show_error_checkbox
        )
        self.preview_header_layout.addWidget(
            self.preview_hide_unchanged_checkbox
        )
        self.preview_header_layout.addWidget(
            self.preview_select_all_button
        )
        self.preview_header_layout.addWidget(
            self.preview_clear_selection_button
        )
        self.preview_header_layout.addWidget(
            self.preview_exclude_selected_button
        )
        self.preview_header_layout.addWidget(
            self.preview_keep_selected_button
        )
        self.preview_header_layout.addWidget(
            self.preview_exclude_error_button
        )
        self.preview_header_layout.addWidget(
            self.preview_export_csv_button
        )
        self.preview_header_layout.addWidget(
            self.preview_export_non_artwork_txt_button
        )
        self.preview_header_layout.addWidget(
            self.preview_export_non_artwork_csv_button
        )
        self.preview_header_layout.addWidget(
            self.preview_scan_selected_button
        )

    def _update_preview_summary(
        self,
        summary: dict,
    ):
        self.preview_summary_label.setText(
            "신규 "
            f"{summary.get('created', 0)} / "
            "업데이트 "
            f"{summary.get('updated', 0)} / "
            "변경 없음 "
            f"{summary.get('unchanged', 0)} / "
            "오류 "
            f"{summary.get('failed', 0)} / "
            "선택 "
            f"{summary.get('selected', 0)}"
        )
