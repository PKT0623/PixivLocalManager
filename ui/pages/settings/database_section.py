from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)


class DatabaseSection(QFrame):
    BACKUP_PATH_ROLE = Qt.UserRole + 1

    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_label = QLabel("데이터 관리")
        title_label.setObjectName("sectionTitle")

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

        auto_backup_title = QLabel("자동 백업")
        auto_backup_title.setObjectName("fieldLabel")

        auto_backup_layout = QHBoxLayout()
        auto_backup_layout.setSpacing(8)

        self.auto_backup_enabled_checkbox = QCheckBox("자동 백업 사용")

        self.backup_interval_input = QSpinBox()
        self.backup_interval_input.setRange(1, 365)
        self.backup_interval_input.setSuffix(" 일")
        self.backup_interval_input.setFixedWidth(100)

        self.backup_keep_count_input = QSpinBox()
        self.backup_keep_count_input.setRange(1, 999)
        self.backup_keep_count_input.setSuffix(" 개")
        self.backup_keep_count_input.setFixedWidth(100)

        self.save_backup_settings_button = QPushButton("백업 설정 저장")
        self.save_backup_settings_button.setObjectName("primaryButton")

        auto_backup_layout.addWidget(self.auto_backup_enabled_checkbox)
        auto_backup_layout.addWidget(QLabel("주기"))
        auto_backup_layout.addWidget(self.backup_interval_input)
        auto_backup_layout.addWidget(QLabel("보관"))
        auto_backup_layout.addWidget(self.backup_keep_count_input)
        auto_backup_layout.addWidget(self.save_backup_settings_button)
        auto_backup_layout.addStretch()

        self.backup_info_label = QLabel("최근 백업: - / 총 백업 용량: -")
        self.backup_info_label.setObjectName("infoText")

        backup_action_layout = QHBoxLayout()
        backup_action_layout.setSpacing(8)

        self.backup_db_button = QPushButton("DB 백업 생성")
        self.restore_db_button = QPushButton("선택 백업 복원")
        self.delete_backup_button = QPushButton("선택 백업 삭제")
        self.refresh_backup_button = QPushButton("목록 새로고침")
        self.open_backup_folder_button = QPushButton("백업 폴더 열기")
        self.export_csv_button = QPushButton("CSV 내보내기")

        backup_action_layout.addWidget(self.backup_db_button)
        backup_action_layout.addWidget(self.restore_db_button)
        backup_action_layout.addWidget(self.delete_backup_button)
        backup_action_layout.addWidget(self.refresh_backup_button)
        backup_action_layout.addWidget(self.open_backup_folder_button)
        backup_action_layout.addWidget(self.export_csv_button)
        backup_action_layout.addStretch()

        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels(
            [
                "파일명",
                "생성일",
                "크기",
                "종류",
            ]
        )
        self.backup_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.backup_table.verticalHeader().setVisible(False)
        self.backup_table.setAlternatingRowColors(True)
        self.backup_table.setMinimumHeight(220)

        header = self.backup_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        layout.addWidget(title_label)
        layout.addWidget(db_path_label)
        layout.addLayout(db_path_layout)
        layout.addLayout(self.db_info_grid)
        layout.addWidget(management_title)
        layout.addLayout(management_action_layout)
        layout.addWidget(self.integrity_result_text)
        layout.addWidget(auto_backup_title)
        layout.addLayout(auto_backup_layout)
        layout.addWidget(self.backup_info_label)
        layout.addLayout(backup_action_layout)
        layout.addWidget(self.backup_table)

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

    def update_backup_table(
        self,
        backups: list,
    ):
        self.backup_table.setRowCount(0)

        for backup in backups:
            row = self.backup_table.rowCount()
            self.backup_table.insertRow(row)

            file_name_item = QTableWidgetItem(backup.file_name)
            file_name_item.setData(
                self.BACKUP_PATH_ROLE,
                backup.file_path,
            )

            created_at_item = QTableWidgetItem(backup.created_at)
            size_item = QTableWidgetItem(backup.size_label)
            type_item = QTableWidgetItem(
                self._format_backup_type(backup.backup_type)
            )

            for item in [
                file_name_item,
                created_at_item,
                size_item,
                type_item,
            ]:
                item.setTextAlignment(Qt.AlignCenter)

            file_name_item.setTextAlignment(
                Qt.AlignVCenter | Qt.AlignLeft
            )

            self.backup_table.setItem(row, 0, file_name_item)
            self.backup_table.setItem(row, 1, created_at_item)
            self.backup_table.setItem(row, 2, size_item)
            self.backup_table.setItem(row, 3, type_item)

    def get_selected_backup_path(self) -> str | None:
        selected_rows = self.backup_table.selectionModel().selectedRows()

        if not selected_rows:
            return None

        row = selected_rows[0].row()
        item = self.backup_table.item(row, 0)

        if item is None:
            return None

        return item.data(self.BACKUP_PATH_ROLE)

    def _create_info_value(self) -> QLabel:
        label = QLabel("-")
        label.setObjectName("infoText")
        return label

    def _add_info_row(
        self,
        layout: QGridLayout,
        row: int,
        label_text: str,
        value_label: QLabel,
    ):
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")

        layout.addWidget(label, row, 0)
        layout.addWidget(value_label, row, 1)

    def _format_backup_type(
        self,
        backup_type: str,
    ) -> str:
        labels = {
            "auto": "자동",
            "manual": "수동",
            "restore_safety": "복원 전 안전백업",
            "unknown": "기타",
        }

        return labels.get(
            backup_type,
            "기타",
        )
