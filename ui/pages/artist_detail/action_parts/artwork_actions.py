import subprocess
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QTableWidgetItem,
    QWidget,
)

from ..utils import (
    calculate_missing_artwork_ids,
    find_recent_local_artworks,
    folder_status_label,
    parse_id_text,
)


class ArtistArtworkActions:
    PIXIV_ARTWORK_URL = "https://www.pixiv.net/artworks/{artwork_id}"

    def copy_folder_path(self):
        artist = self.page.current_artist

        if artist is None:
            return

        folder_path = str(artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        QApplication.clipboard().setText(folder_path)

    def copy_pixiv_id(self):
        artist = self.page.current_artist

        if artist is None:
            return

        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        QApplication.clipboard().setText(pixiv_id)

    def open_all_missing_artworks(self):
        artwork_ids = self.get_all_artwork_ids(
            self.page.info_section.missing_artwork_table,
            0,
        )

        self.open_pixiv_artworks(artwork_ids)

    def get_all_artwork_ids(self, table, column: int) -> list[str]:
        artwork_ids = []

        for row in range(table.rowCount()):
            item = table.item(row, column)

            if item is None:
                continue

            artwork_id = item.text().strip()

            if artwork_id:
                artwork_ids.append(artwork_id)

        return artwork_ids

    def open_pixiv_artwork(self, artwork_id: str):
        artwork_id = str(artwork_id or "").strip()

        if not artwork_id:
            return

        webbrowser.open(
            self.PIXIV_ARTWORK_URL.format(
                artwork_id=artwork_id,
            )
        )

    def open_pixiv_artworks(self, artwork_ids: list[str]):
        if not artwork_ids:
            return

        for artwork_id in artwork_ids:
            self.open_pixiv_artwork(artwork_id)

    def open_recent_artwork_folder(self, file_path: str):
        file_path = str(file_path or "").strip()

        if not file_path:
            return

        path = Path(file_path)

        if not path.exists():
            self.show_warning(
                "폴더 이동 오류",
                "파일을 찾을 수 없습니다.",
            )
            return

        try:
            subprocess.Popen(
                f'explorer.exe /select,"{path}"',
                shell=True,
            )
        except Exception:
            try:
                subprocess.Popen(
                    f'explorer.exe "{path.parent}"',
                    shell=True,
                )
            except Exception as error:
                self.show_warning(
                    "폴더 이동 오류",
                    f"파일 위치를 열지 못했습니다.\n{error}",
                )

    def set_missing_artwork_table_data(self, artist: dict):
        section = self.page.info_section
        table = section.missing_artwork_table
        table.setRowCount(0)

        local_ids = parse_id_text(
            artist.get("local_latest_artwork_ids", "")
        )
        pixiv_ids = parse_id_text(
            artist.get("pixiv_latest_artwork_ids", "")
        )
        missing_ids = calculate_missing_artwork_ids(
            local_ids,
            pixiv_ids,
        )

        section.missing_artwork_count_label.setText(
            f"누락 작품 ID 목록 ({len(missing_ids)}개)"
        )

        for artwork_id in missing_ids:
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(
                row,
                0,
                self.create_readonly_item(artwork_id),
            )

            pixiv_button = self.create_small_button("이동")
            pixiv_button.clicked.connect(
                lambda checked=False, aid=artwork_id: (
                    self.open_pixiv_artwork(aid)
                )
            )

            table.setCellWidget(
                row,
                1,
                self.create_centered_widget(pixiv_button),
            )

    def set_recent_local_artwork_table_data(self, folder_path: str):
        section = self.page.info_section
        table = section.recent_local_artwork_table
        table.setRowCount(0)

        artworks = find_recent_local_artworks(
            folder_path,
            limit=10,
        )

        for artwork in artworks:
            row = table.rowCount()
            table.insertRow(row)

            artwork_id = artwork["artwork_id"]
            file_path = artwork["file_path"]

            table.setItem(
                row,
                0,
                self.create_readonly_item(artwork_id),
            )
            table.setItem(
                row,
                1,
                self.create_readonly_item(str(artwork["file_count"])),
            )
            table.setItem(
                row,
                2,
                self.create_readonly_item(artwork["latest_modified_at"]),
            )

            pixiv_button = self.create_small_button("Pixiv")
            pixiv_button.clicked.connect(
                lambda checked=False, aid=artwork_id: (
                    self.open_pixiv_artwork(aid)
                )
            )

            folder_button = self.create_small_button("폴더")
            folder_button.clicked.connect(
                lambda checked=False, path=file_path: (
                    self.open_recent_artwork_folder(path)
                )
            )

            shortcut_widget = self.create_shortcut_widget(
                pixiv_button,
                folder_button,
            )

            table.setCellWidget(row, 3, shortcut_widget)

    def create_readonly_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        return item

    def create_small_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("smallActionButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(60, 24)

        return button

    def create_centered_widget(self, widget) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()

        return container

    def create_shortcut_widget(self, *buttons) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        layout.addStretch()

        for button in buttons:
            layout.addWidget(button)

        layout.addStretch()

        return container

    def select_folder(self):
        current_path = self.page.info_section.folder_path_input.text().strip()

        if current_path == "-":
            current_path = ""

        folder_path = QFileDialog.getExistingDirectory(
            self.page,
            "작가 폴더 선택",
            current_path,
        )

        if not folder_path:
            return

        self.page.info_section.folder_path_input.setText(folder_path)
        self.page.info_section.folder_status_label.setText(
            folder_status_label(folder_path)
        )

        self.set_recent_local_artwork_table_data(folder_path)
