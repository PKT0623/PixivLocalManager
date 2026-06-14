from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class DatabaseSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("데이터 관리")
        title_label.setObjectName("sectionTitle")

        db_path_label = QLabel("DB 파일 위치")
        db_path_label.setObjectName("fieldLabel")

        db_path_layout = QHBoxLayout()
        db_path_layout.setSpacing(8)

        self.db_path_input = QLineEdit()
        self.db_path_input.setReadOnly(True)

        self.open_db_folder_button = QPushButton("폴더 열기")

        db_path_layout.addWidget(self.db_path_input, 1)
        db_path_layout.addWidget(self.open_db_folder_button)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.backup_db_button = QPushButton("DB 백업")
        self.restore_db_button = QPushButton("DB 복원")
        self.export_csv_button = QPushButton("CSV 내보내기")

        action_layout.addWidget(self.backup_db_button)
        action_layout.addWidget(self.restore_db_button)
        action_layout.addWidget(self.export_csv_button)
        action_layout.addStretch()

        layout.addWidget(title_label)
        layout.addWidget(db_path_label)
        layout.addLayout(db_path_layout)
        layout.addLayout(action_layout)
