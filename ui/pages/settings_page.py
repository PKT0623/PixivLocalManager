import csv
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.database.connection import DB_PATH
from app.services.artist_service import ArtistService
from app.services.settings_service import SettingsService


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.settings_service = SettingsService()
        self.artist_service = ArtistService()

        self._setup_ui()
        self._connect_signals()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title_label = QLabel("설정")
        title_label.setObjectName("pageTitle")

        description_label = QLabel(
            "DB 경로, 백업, 내보내기 같은 프로그램 설정을 관리하는 화면입니다."
        )
        description_label.setObjectName("pageDescription")

        folder_frame = self._create_folder_frame()
        pixiv_frame = self._create_pixiv_frame()
        db_frame = self._create_db_frame()
        app_frame = self._create_app_info_frame()

        self.status_label = QLabel("준비됨")
        self.status_label.setObjectName("statusLabel")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(folder_frame)
        layout.addWidget(pixiv_frame)
        layout.addWidget(db_frame)
        layout.addWidget(app_frame)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setStyleSheet(
            """
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#pageDescription {
                font-size: 15px;
                color: #666666;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#fieldLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333333;
            }

            QLabel#statusLabel {
                font-size: 14px;
                color: #198754;
                padding-top: 4px;
            }

            QLabel#infoText {
                font-size: 14px;
                color: #555555;
            }

            QFrame#settingFrame {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
            }

            QLineEdit {
                border: 1px solid #dddddd;
                border-radius: 6px;
                padding: 8px 10px;
                background-color: #ffffff;
                font-size: 14px;
            }

            QLineEdit:read-only {
                background-color: #f9f9f9;
                color: #555555;
            }

            QPushButton {
                padding: 8px 14px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#primaryButton {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
            }

            QPushButton#primaryButton:hover {
                background-color: #157347;
            }
            """
        )

    def _create_folder_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("settingFrame")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("기본 폴더")
        title_label.setObjectName("sectionTitle")

        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)

        self.pixiv_root_input = QLineEdit()
        self.pixiv_root_input.setReadOnly(True)
        self.pixiv_root_input.setPlaceholderText("기본 Pixiv 폴더를 선택하세요.")

        self.select_pixiv_root_button = QPushButton("폴더 선택")
        self.save_pixiv_root_button = QPushButton("저장")
        self.save_pixiv_root_button.setObjectName("primaryButton")

        row_layout.addWidget(self.pixiv_root_input, 1)
        row_layout.addWidget(self.select_pixiv_root_button)
        row_layout.addWidget(self.save_pixiv_root_button)

        layout.addWidget(title_label)
        layout.addLayout(row_layout)

        return frame

    def _create_pixiv_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("settingFrame")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("Pixiv 연동")
        title_label.setObjectName("sectionTitle")

        cookie_label = QLabel("PHPSESSID")
        cookie_label.setObjectName("fieldLabel")

        cookie_layout = QHBoxLayout()
        cookie_layout.setSpacing(8)

        self.phpsessid_input = QLineEdit()
        self.phpsessid_input.setEchoMode(QLineEdit.Password)
        self.phpsessid_input.setPlaceholderText("Pixiv PHPSESSID를 입력하세요.")

        self.save_phpsessid_button = QPushButton("저장")
        self.save_phpsessid_button.setObjectName("primaryButton")

        cookie_layout.addWidget(self.phpsessid_input, 1)
        cookie_layout.addWidget(self.save_phpsessid_button)

        self.phpsessid_status_label = QLabel("저장된 PHPSESSID 없음")
        self.phpsessid_status_label.setObjectName("infoText")

        layout.addWidget(title_label)
        layout.addWidget(cookie_label)
        layout.addLayout(cookie_layout)
        layout.addWidget(self.phpsessid_status_label)

        return frame

    def _create_db_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("settingFrame")

        layout = QVBoxLayout(frame)
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

        return frame

    def _create_app_info_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("settingFrame")

        layout = QGridLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(8)

        title_label = QLabel("프로그램 정보")
        title_label.setObjectName("sectionTitle")

        app_name_label = QLabel("프로그램")
        app_name_label.setObjectName("fieldLabel")

        app_name_value = QLabel("Pixiv Local Manager")
        app_name_value.setObjectName("infoText")

        version_label = QLabel("버전")
        version_label.setObjectName("fieldLabel")

        version_value = QLabel("0.1.0")
        version_value.setObjectName("infoText")

        stack_label = QLabel("기술 스택")
        stack_label.setObjectName("fieldLabel")

        stack_value = QLabel("Python / PySide6 / SQLite")
        stack_value.setObjectName("infoText")

        layout.addWidget(title_label, 0, 0, 1, 2)
        layout.addWidget(app_name_label, 1, 0)
        layout.addWidget(app_name_value, 1, 1)
        layout.addWidget(version_label, 2, 0)
        layout.addWidget(version_value, 2, 1)
        layout.addWidget(stack_label, 3, 0)
        layout.addWidget(stack_value, 3, 1)

        return frame

    def _connect_signals(self):
        self.select_pixiv_root_button.clicked.connect(
            self._select_pixiv_root_folder
        )
        self.save_pixiv_root_button.clicked.connect(
            self._save_pixiv_root_folder
        )
        self.save_phpsessid_button.clicked.connect(
            self._save_phpsessid
        )
        self.open_db_folder_button.clicked.connect(
            self._open_db_folder
        )
        self.backup_db_button.clicked.connect(
            self._backup_database
        )
        self.restore_db_button.clicked.connect(
            self._restore_database
        )
        self.export_csv_button.clicked.connect(
            self._export_artists_csv
        )

    def _load_settings(self):
        pixiv_root_folder = self.settings_service.get_setting(
            "pixiv_root_folder"
        )

        if pixiv_root_folder:
            self.pixiv_root_input.setText(pixiv_root_folder)

        phpsessid = self.settings_service.get_setting(
            "pixiv_phpsessid"
        )

        if phpsessid:
            self.phpsessid_input.setText(phpsessid)
            self.phpsessid_status_label.setText(
                f"저장됨: {self._mask_secret(phpsessid)}"
            )

        db_path = self._get_database_path()
        self.db_path_input.setText(str(db_path))

    def _select_pixiv_root_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "기본 Pixiv 폴더 선택",
            self.pixiv_root_input.text().strip(),
        )

        if not folder_path:
            return

        self.pixiv_root_input.setText(folder_path)
        self._set_status("기본 Pixiv 폴더를 선택했습니다. 저장 버튼을 눌러 반영하세요.")

    def _save_pixiv_root_folder(self):
        folder_path = self.pixiv_root_input.text().strip()

        if not folder_path:
            self._set_status("저장할 Pixiv 폴더가 없습니다.", error=True)
            return

        try:
            self.settings_service.set_setting(
                "pixiv_root_folder",
                folder_path,
            )
        except Exception as error:
            self._set_status(f"기본 Pixiv 폴더 저장 실패: {error}", error=True)
            return

        self._set_status("기본 Pixiv 폴더가 저장되었습니다.")

    def _save_phpsessid(self):
        phpsessid = self.phpsessid_input.text().strip()

        if not phpsessid:
            self._set_status("저장할 PHPSESSID가 없습니다.", error=True)
            return

        try:
            self.settings_service.set_setting(
                "pixiv_phpsessid",
                phpsessid,
            )
        except Exception as error:
            self._set_status(f"PHPSESSID 저장 실패: {error}", error=True)
            return

        self.phpsessid_status_label.setText(
            f"저장됨: {self._mask_secret(phpsessid)}"
        )
        self._set_status("Pixiv PHPSESSID가 저장되었습니다.")

    def _open_db_folder(self):
        db_path = self._get_database_path()

        if not db_path.exists():
            self._set_status("DB 파일을 찾을 수 없습니다.", error=True)
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(db_path.parent))
        )

    def _backup_database(self):
        db_path = self._get_database_path()

        if not db_path.exists():
            self._set_status("백업할 DB 파일을 찾을 수 없습니다.", error=True)
            return

        if not self._is_valid_sqlite_database(db_path):
            self._set_status(
                "DB 백업 실패: 현재 DB 파일이 유효한 SQLite DB가 아닙니다.",
                error=True,
            )
            return

        backup_folder = QFileDialog.getExistingDirectory(
            self,
            "DB 백업 폴더 선택",
            str(db_path.parent),
        )

        if not backup_folder:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(backup_folder) / f"pixiv_manager_backup_{timestamp}.db"

        try:
            shutil.copy2(db_path, backup_path)
        except OSError as error:
            self._set_status(f"DB 백업 실패: {error}", error=True)
            return

        self._set_status(f"DB 백업 완료: {backup_path}")

    def _restore_database(self):
        db_path = self._get_database_path()

        restore_file, _ = QFileDialog.getOpenFileName(
            self,
            "복원할 DB 파일 선택",
            str(db_path.parent),
            "SQLite DB (*.db);;All Files (*)",
        )

        if not restore_file:
            return

        restore_path = Path(restore_file)

        if not self._is_valid_sqlite_database(restore_path):
            self._set_status(
                "DB 복원 실패: 유효한 SQLite DB 파일이 아닙니다.",
                error=True,
            )
            return

        try:
            if db_path.exists() and self._is_valid_sqlite_database(db_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_backup_path = (
                    db_path.parent / f"pixiv_manager_before_restore_{timestamp}.db"
                )
                shutil.copy2(db_path, safe_backup_path)

            shutil.copy2(restore_path, db_path)
        except OSError as error:
            self._set_status(f"DB 복원 실패: {error}", error=True)
            return

        self._set_status("DB 복원이 완료되었습니다. 프로그램을 재시작하세요.")

    def _export_artists_csv(self):
        export_file, _ = QFileDialog.getSaveFileName(
            self,
            "작가 목록 CSV 내보내기",
            "artists.csv",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not export_file:
            return

        if not export_file.lower().endswith(".csv"):
            export_file += ".csv"

        artists = self.artist_service.get_all_artists()

        fieldnames = [
            "id",
            "artist_name",
            "pixiv_id",
            "folder_path",
            "folder_artwork_count",
            "folder_file_count",
            "rating",
            "status",
            "update_status",
            "memo",
            "created_at",
            "updated_at",
        ]

        try:
            with open(
                export_file,
                "w",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=fieldnames,
                    extrasaction="ignore",
                )
                writer.writeheader()
                writer.writerows(artists)
        except OSError as error:
            self._set_status(f"CSV 내보내기 실패: {error}", error=True)
            return

        self._set_status(f"CSV 내보내기 완료: {export_file}")

    def _get_database_path(self) -> Path:
        return DB_PATH

    def _is_valid_sqlite_database(self, file_path: Path) -> bool:
        try:
            with open(file_path, "rb") as db_file:
                header = db_file.read(16)

            if not header.startswith(b"SQLite format 3"):
                return False

            with sqlite3.connect(file_path) as conn:
                result = conn.execute(
                    "PRAGMA integrity_check"
                ).fetchone()

            return result is not None and result[0] == "ok"
        except (OSError, sqlite3.DatabaseError):
            return False

    def _mask_secret(self, value: str) -> str:
        if len(value) <= 8:
            return "*" * len(value)

        return f"{value[:4]}{'*' * 8}{value[-4:]}"

    def _set_status(self, message: str, error: bool = False):
        self.status_label.setText(message)

        if error:
            self.status_label.setStyleSheet("color: #dc3545;")
            return

        self.status_label.setStyleSheet("color: #198754;")
