from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)


class LogSection(QFrame):
    LOG_PATH_ROLE = Qt.UserRole + 1

    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_label = QLabel("로그 관리")
        title_label.setObjectName("sectionTitle")

        description_label = QLabel(
            "logs 폴더와 data/logs 폴더의 로그 파일을 조회하고 삭제합니다."
        )
        description_label.setObjectName("infoText")

        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.refresh_log_button = QPushButton("로그 새로고침")
        self.open_log_folder_button = QPushButton("로그 폴더 열기")
        self.delete_selected_log_button = QPushButton("선택 로그 삭제")
        self.delete_all_logs_button = QPushButton("전체 로그 삭제")
        self.delete_all_logs_button.setObjectName("dangerButton")

        action_layout.addWidget(self.refresh_log_button)
        action_layout.addWidget(self.open_log_folder_button)
        action_layout.addWidget(self.delete_selected_log_button)
        action_layout.addWidget(self.delete_all_logs_button)
        action_layout.addStretch()

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(
            [
                "파일명",
                "구분",
                "수정일",
                "크기",
            ]
        )
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.log_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setMinimumHeight(220)

        header = self.log_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.log_content_text = QTextEdit()
        self.log_content_text.setReadOnly(True)
        self.log_content_text.setMinimumHeight(220)
        self.log_content_text.setPlaceholderText(
            "로그를 선택하면 내용이 여기에 표시됩니다."
        )

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addLayout(action_layout)
        layout.addWidget(self.log_table)
        layout.addWidget(self.log_content_text)

    def update_log_table(
        self,
        logs: list,
    ):
        self.log_table.setRowCount(0)

        for log in logs:
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)

            file_name_item = self._create_item(log.file_name)
            file_name_item.setData(
                self.LOG_PATH_ROLE,
                log.file_path,
            )

            category_item = self._create_item(log.category)
            modified_at_item = self._create_item(log.modified_at)
            size_item = self._create_item(log.size_label)

            file_name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            self.log_table.setItem(row, 0, file_name_item)
            self.log_table.setItem(row, 1, category_item)
            self.log_table.setItem(row, 2, modified_at_item)
            self.log_table.setItem(row, 3, size_item)

    def get_selected_log_path(self) -> str | None:
        selected_rows = self.log_table.selectionModel().selectedRows()

        if not selected_rows:
            return None

        row = selected_rows[0].row()
        item = self.log_table.item(row, 0)

        if item is None:
            return None

        return item.data(self.LOG_PATH_ROLE)

    def set_log_content(
        self,
        text: str,
    ):
        self.log_content_text.setPlainText(text)

    def clear_log_content(self):
        self.log_content_text.clear()

    def _create_item(
        self,
        value: str,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        return item

