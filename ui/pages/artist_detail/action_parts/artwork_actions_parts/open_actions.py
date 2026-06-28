import subprocess
import webbrowser
from pathlib import Path


class ArtworkOpenActionsMixin:
    def open_artist_pixiv(self):
        artist = self.page.current_artist

        if artist is None:
            return

        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        webbrowser.open(
            self.PIXIV_ARTIST_URL.format(
                pixiv_id=pixiv_id,
            )
        )

    def open_artist_folder(self):
        artist = self.page.current_artist

        if artist is None:
            return

        folder_path = str(artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        path = Path(folder_path)

        if not path.exists() or not path.is_dir():
            self.show_warning(
                "폴더 열기 오류",
                "작가 폴더를 찾을 수 없습니다.",
            )
            return

        try:
            subprocess.Popen(
                f'explorer.exe "{path}"',
                shell=True,
            )
        except Exception as error:
            self.show_warning(
                "폴더 열기 오류",
                f"작가 폴더를 열지 못했습니다.\n{error}",
            )

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
