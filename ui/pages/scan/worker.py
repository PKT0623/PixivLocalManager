from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.services.artist_service import ArtistService


class ScanWorker(QObject):
    log_message_requested = Signal(str)
    scan_result_requested = Signal(dict)
    progress_updated = Signal(int, int)
    current_folder_changed = Signal(str)
    target_count_changed = Signal(int)
    finished = Signal()
    failed = Signal(str)

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    def __init__(self, root_folder_path: str):
        super().__init__()

        self.root_folder_path = root_folder_path
        self.artist_service = ArtistService()

    def run(self):
        try:
            root_folder = Path(self.root_folder_path)

            if not root_folder.exists() or not root_folder.is_dir():
                raise ValueError("선택한 폴더가 존재하지 않습니다.")

            self.log_message_requested.emit("작가 폴더 탐색을 시작합니다.")
            artist_folders = self._find_artist_folders(root_folder)

            self.target_count_changed.emit(len(artist_folders))
            self.progress_updated.emit(0, len(artist_folders))

            if not artist_folders:
                self.log_message_requested.emit(
                    "이미지 파일이 있는 작가 폴더를 찾지 못했습니다."
                )
                self.finished.emit()
                return

            self.log_message_requested.emit(
                f"발견된 작가 폴더: {len(artist_folders)}개"
            )

            created_count = 0
            updated_count = 0
            fail_count = 0

            for index, folder_path in enumerate(
                artist_folders,
                start=1,
            ):
                self.current_folder_changed.emit(folder_path.name)

                try:
                    result = self._scan_artist_folder(folder_path)
                    action = result.get("action")
                    artist = result.get("artist") or {}

                    if action == "created":
                        created_count += 1
                        result_label = "등록"
                    else:
                        updated_count += 1
                        result_label = "업데이트"

                    self.scan_result_requested.emit(
                        self._build_scan_result_row(
                            index=index,
                            total=len(artist_folders),
                            result=result_label,
                            artist=artist,
                        )
                    )
                except Exception as error:
                    fail_count += 1
                    self.scan_result_requested.emit(
                        {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "progress": f"{index}/{len(artist_folders)}",
                            "result": "실패",
                            "artist_name": folder_path.name,
                            "pixiv_id": "-",
                            "artwork_count": "-",
                            "file_count": "-",
                            "update_status": str(error),
                        }
                    )

                self.progress_updated.emit(
                    index,
                    len(artist_folders),
                )

            self.current_folder_changed.emit("-")
            self.log_message_requested.emit(
                "전체 스캔 완료: "
                f"등록 {created_count}개, "
                f"업데이트 {updated_count}개, "
                f"실패 {fail_count}개"
            )
        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit()

    def _find_artist_folders(self, root_folder: Path) -> list[Path]:
        artist_folders = []

        for folder_path in self._iter_folders(
            root_folder,
            max_depth=3,
        ):
            if self._has_image_files(folder_path):
                artist_folders.append(folder_path)

        artist_folders = sorted(
            set(artist_folders),
            key=lambda path: str(path).lower(),
        )

        return artist_folders

    def _iter_folders(
        self,
        root_folder: Path,
        max_depth: int,
    ) -> list[Path]:
        folders = []

        def walk(
            current_folder: Path,
            depth: int,
        ):
            if depth > max_depth:
                return

            try:
                child_folders = [
                    path
                    for path in current_folder.iterdir()
                    if path.is_dir()
                ]
            except OSError:
                return

            for child_folder in child_folders:
                folders.append(child_folder)
                walk(child_folder, depth + 1)

        walk(root_folder, 1)

        if self._has_image_files(root_folder):
            folders.insert(0, root_folder)

        return folders

    def _has_image_files(self, folder_path: Path) -> bool:
        try:
            for file_path in folder_path.iterdir():
                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() in self.IMAGE_EXTENSIONS:
                    return True
        except OSError:
            return False

        return False

    def _scan_artist_folder(self, folder_path: Path) -> dict:
        return self.artist_service.save_scanned_artist(
            str(folder_path)
        )

    def _build_scan_result_row(
        self,
        index: int,
        total: int,
        result: str,
        artist: dict,
    ) -> dict:
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": f"{index}/{total}",
            "result": result,
            "artist_name": str(artist.get("artist_name", "") or "-"),
            "pixiv_id": str(artist.get("pixiv_id", "") or "-"),
            "artwork_count": str(artist.get("folder_artwork_count", 0)),
            "file_count": str(artist.get("folder_file_count", 0)),
            "update_status": str(artist.get("update_status", "") or "-"),
        }
