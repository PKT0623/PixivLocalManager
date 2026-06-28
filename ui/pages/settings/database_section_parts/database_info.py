from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
)


class DatabaseInfoMixin:
    def _create_database_info_section(self):
        db_path_label = QLabel("DB 파일 위치")
        db_path_label.setObjectName("fieldLabel")

        db_path_layout = QHBoxLayout()
        db_path_layout.setSpacing(8)

        self.db_path_input = QLineEdit()
        self.db_path_input.setReadOnly(True)

        self.open_db_folder_button = QPushButton("DB 폴더 열기")

        db_path_layout.addWidget(self.db_path_input, 1)
        db_path_layout.addWidget(self.open_db_folder_button)

        self.db_info_grid = QGridLayout()
        self.db_info_grid.setHorizontalSpacing(16)
        self.db_info_grid.setVerticalSpacing(8)

        self.db_size_value = self._create_info_value()
        self.artist_count_value = self._create_info_value()
        self.settings_count_value = self._create_info_value()
        self.update_history_count_value = self._create_info_value()
        self.total_artworks_value = self._create_info_value()
        self.total_files_value = self._create_info_value()
        self.total_folder_size_value = self._create_info_value()

        self._add_info_row(
            self.db_info_grid,
            0,
            "DB 크기",
            self.db_size_value,
        )
        self._add_info_row(
            self.db_info_grid,
            1,
            "작가 수",
            self.artist_count_value,
        )
        self._add_info_row(
            self.db_info_grid,
            2,
            "설정 수",
            self.settings_count_value,
        )
        self._add_info_row(
            self.db_info_grid,
            3,
            "업데이트 이력 수",
            self.update_history_count_value,
        )
        self._add_info_row(
            self.db_info_grid,
            4,
            "전체 작품 수",
            self.total_artworks_value,
        )
        self._add_info_row(
            self.db_info_grid,
            5,
            "전체 파일 수",
            self.total_files_value,
        )
        self._add_info_row(
            self.db_info_grid,
            6,
            "전체 폴더 용량",
            self.total_folder_size_value,
        )

        management_title = QLabel("DB 검사 / 최적화")
        management_title.setObjectName("fieldLabel")

        management_action_layout = QHBoxLayout()
        management_action_layout.setSpacing(8)

        self.check_integrity_button = QPushButton("무결성 검사")
        self.optimize_db_button = QPushButton("DB 최적화")
        self.refresh_db_info_button = QPushButton("DB 정보 새로고침")

        management_action_layout.addWidget(self.check_integrity_button)
        management_action_layout.addWidget(self.optimize_db_button)
        management_action_layout.addWidget(self.refresh_db_info_button)
        management_action_layout.addStretch()

        self.integrity_result_text = QTextEdit()
        self.integrity_result_text.setReadOnly(True)
        self.integrity_result_text.setMinimumHeight(130)
        self.integrity_result_text.setPlaceholderText(
            "무결성 검사 결과가 여기에 표시됩니다."
        )

        return (
            db_path_label,
            db_path_layout,
            self.db_info_grid,
            management_title,
            management_action_layout,
            self.integrity_result_text,
        )

    def update_database_info(
        self,
        info: dict,
    ):
        self.db_path_input.setText(info.get("db_path", "-"))
        self.db_size_value.setText(info.get("db_size", "-"))
        self.artist_count_value.setText(
            f"{info.get('artist_count', 0)}명"
        )
        self.settings_count_value.setText(
            f"{info.get('settings_count', 0)}개"
        )
        self.update_history_count_value.setText(
            f"{info.get('update_history_count', 0)}건"
        )
        self.total_artworks_value.setText(
            f"{info.get('total_artworks', 0)}개"
        )
        self.total_files_value.setText(
            f"{info.get('total_files', 0)}개"
        )
        self.total_folder_size_value.setText(
            info.get("total_folder_size", "-")
        )

    def update_integrity_result(
        self,
        text: str,
    ):
        self.integrity_result_text.setPlainText(text)
