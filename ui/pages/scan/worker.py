from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.services.artist_service import ArtistService

from .folder_scanner import FolderScanner


class ScanWorker(QObject):
    log_message_requested = Signal(str)
    scan_result_requested = Signal(dict)
    progress_updated = Signal(int, int)
    current_folder_changed = Signal(str)
    target_count_changed = Signal(int)
    summary_updated = Signal(dict)
    finished = Signal()
    failed = Signal(str)

    def __init__(
        self,
        root_folder_path: str,
        target_folder_paths: list[str] | None = None,
    ):
        super().__init__()

        self.root_folder_path = root_folder_path
        self.target_folder_paths = target_folder_paths
        self.artist_service = ArtistService()
        self.folder_scanner = FolderScanner()

    def run(self):
        try:
            artist_folders = self._get_artist_folders()

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

            summary = {
                "created": 0,
                "updated": 0,
                "unchanged": 0,
                "failed": 0,
            }
            self.summary_updated.emit(summary)

            for index, folder_path in enumerate(
                artist_folders,
                start=1,
            ):
                self.current_folder_changed.emit(folder_path.name)

                try:
                    result = self._scan_artist_folder(folder_path)
                    action = result.get("action")
                    artist = result.get("artist") or {}

                    result_label = self._result_label(action)
                    self._increase_summary(summary, action)

                    self.scan_result_requested.emit(
                        self._build_scan_result_row(
                            index=index,
                            total=len(artist_folders),
                            result=result_label,
                            artist=artist,
                            folder_path=folder_path,
                        )
                    )
                except Exception as error:
                    summary["failed"] += 1

                    self.scan_result_requested.emit(
                        self._build_failed_result_row(
                            index=index,
                            total=len(artist_folders),
                            folder_path=folder_path,
                            error=error,
                        )
                    )

                self.summary_updated.emit(summary)
                self.progress_updated.emit(
                    index,
                    len(artist_folders),
                )

            self.current_folder_changed.emit("-")
            self.log_message_requested.emit(
                "전체 스캔 완료: "
                f"등록 {summary['created']}개, "
                f"업데이트 {summary['updated']}개, "
                f"변경 없음 {summary['unchanged']}개, "
                f"실패 {summary['failed']}개"
            )
        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit()

    def _get_artist_folders(self) -> list[Path]:
        if self.target_folder_paths is not None:
            return [
                Path(folder_path)
                for folder_path in self.target_folder_paths
                if str(folder_path or "").strip()
            ]

        root_folder = Path(self.root_folder_path)

        if not root_folder.exists() or not root_folder.is_dir():
            raise ValueError("선택한 폴더가 존재하지 않습니다.")

        return self.folder_scanner.find_artist_folders(
            root_folder,
            max_depth=3,
        )

    def _scan_artist_folder(self, folder_path: Path) -> dict:
        return self.artist_service.save_scanned_artist(
            str(folder_path)
        )

    def _result_label(self, action: str | None) -> str:
        if action == "created":
            return "등록"

        if action == "updated":
            return "업데이트"

        if action == "unchanged":
            return "변경 없음"

        return "업데이트"

    def _increase_summary(
        self,
        summary: dict,
        action: str | None,
    ):
        if action == "created":
            summary["created"] += 1
            return

        if action == "updated":
            summary["updated"] += 1
            return

        if action == "unchanged":
            summary["unchanged"] += 1
            return

        summary["updated"] += 1

    def _build_scan_result_row(
        self,
        index: int,
        total: int,
        result: str,
        artist: dict,
        folder_path: Path,
    ) -> dict:
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": f"{index}/{total}",
            "result": result,
            "artist_id": artist.get("id"),
            "artist_name": str(artist.get("artist_name", "") or "-"),
            "pixiv_id": str(artist.get("pixiv_id", "") or "-"),
            "artwork_count": str(artist.get("folder_artwork_count", 0)),
            "file_count": str(artist.get("folder_file_count", 0)),
            "update_status": str(artist.get("update_status", "") or "-"),
            "folder_path": str(folder_path),
            "error_message": "-",
        }

    def _build_failed_result_row(
        self,
        index: int,
        total: int,
        folder_path: Path,
        error: Exception,
    ) -> dict:
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": f"{index}/{total}",
            "result": "실패",
            "artist_id": None,
            "artist_name": folder_path.name,
            "pixiv_id": "-",
            "artwork_count": "-",
            "file_count": "-",
            "update_status": "error",
            "folder_path": str(folder_path),
            "error_message": str(error),
        }
