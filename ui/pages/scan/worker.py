from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.services.artist_service import ArtistService
from app.services.folder_scan_service import FolderScanService

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
        self.folder_scan_service = FolderScanService()

    def run(self):
        try:
            artist_folders = self._get_artist_folders()
            validation_result = self._validate_artist_folders(artist_folders)

            for row_data in validation_result["log_rows"]:
                self.scan_result_requested.emit(row_data)

            artist_folders = validation_result["scannable_folders"]

            self.target_count_changed.emit(len(artist_folders))
            self.progress_updated.emit(0, len(artist_folders))

            if not artist_folders:
                self.log_message_requested.emit(
                    "스캔 가능한 작가 폴더가 없습니다."
                )
                self.finished.emit()
                return

            self.log_message_requested.emit(
                f"스캔 대상 작가 폴더: {len(artist_folders)}개"
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

    def _validate_artist_folders(
        self,
        artist_folders: list[Path],
    ) -> dict:
        log_rows = []
        scannable_folders = []
        registered_pixiv_ids = set()

        seen_folder_paths = set()
        seen_pixiv_ids = set()
        existing_artists = self.artist_service.get_all_artists()
        existing_by_pixiv_id = self._build_existing_pixiv_id_map(
            existing_artists
        )
        existing_by_folder_path = self._build_existing_folder_path_map(
            existing_artists
        )

        total = len(artist_folders)

        for index, folder_path in enumerate(artist_folders, start=1):
            result = self._validate_artist_folder(
                folder_path=folder_path,
                index=index,
                total=total,
                seen_folder_paths=seen_folder_paths,
                seen_pixiv_ids=seen_pixiv_ids,
                existing_by_pixiv_id=existing_by_pixiv_id,
                existing_by_folder_path=existing_by_folder_path,
                registered_pixiv_ids=registered_pixiv_ids,
            )

            log_rows.extend(result["log_rows"])

            if result["can_scan"]:
                scannable_folders.append(folder_path)

        if registered_pixiv_ids:
            log_rows.append(
                self._build_validation_row(
                    index=0,
                    total=total,
                    result="경고",
                    artist_name="이미 등록된 Pixiv ID",
                    pixiv_id="-",
                    folder_path=Path(self.root_folder_path),
                    message=(
                        f"이미 등록된 Pixiv ID "
                        f"{len(registered_pixiv_ids)}개를 발견했습니다. "
                        "해당 항목은 기존 작가 정보 갱신 대상으로 "
                        "처리합니다."
                    ),
                )
            )

        return {
            "log_rows": log_rows,
            "scannable_folders": scannable_folders,
        }

    def _validate_artist_folder(
        self,
        folder_path: Path,
        index: int,
        total: int,
        seen_folder_paths: set[str],
        seen_pixiv_ids: set[str],
        existing_by_pixiv_id: dict[str, dict],
        existing_by_folder_path: dict[str, dict],
        registered_pixiv_ids: set[str],
    ) -> dict:
        log_rows = []
        folder_key = str(folder_path.resolve()).casefold()
        artist_name = folder_path.name
        pixiv_id = "-"
        can_scan = True

        if folder_key in seen_folder_paths:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="중복 폴더 경로입니다. 이후 항목은 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        seen_folder_paths.add(folder_key)

        if not folder_path.exists():
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="폴더를 찾을 수 없습니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        if not folder_path.is_dir():
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="폴더 경로가 아닙니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        if not self.folder_scanner.has_image_files(folder_path):
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="이미지 파일이 없습니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        artist_name, pixiv_id = (
            self.folder_scan_service.parse_artist_folder_name(
                folder_path.name
            )
        )
        rule_status = self.folder_scan_service.get_folder_name_rule_status(
            folder_path.name
        )

        if not pixiv_id:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name or folder_path.name,
                    pixiv_id="-",
                    folder_path=folder_path,
                    message="Pixiv ID가 없습니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        if not artist_name:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=folder_path.name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message="작가명을 찾을 수 없습니다. 스캔에서 제외합니다.",
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        if pixiv_id in seen_pixiv_ids:
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="오류",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message=(
                        "이번 스캔 대상 안에서 중복 Pixiv ID가 발견됐습니다. "
                        "이후 항목은 제외합니다."
                    ),
                )
            )
            return {
                "can_scan": False,
                "log_rows": log_rows,
            }

        seen_pixiv_ids.add(pixiv_id)

        if rule_status["level"] == "warning":
            log_rows.append(
                self._build_validation_row(
                    index=index,
                    total=total,
                    result="경고",
                    artist_name=artist_name,
                    pixiv_id=pixiv_id,
                    folder_path=folder_path,
                    message=rule_status["message"],
                )
            )

        existing_by_folder = existing_by_folder_path.get(folder_key)

        if existing_by_folder is not None:
            existing_pixiv_id = str(existing_by_folder.get("pixiv_id", ""))

            if existing_pixiv_id != pixiv_id:
                log_rows.append(
                    self._build_validation_row(
                        index=index,
                        total=total,
                        result="오류",
                        artist_name=artist_name,
                        pixiv_id=pixiv_id,
                        folder_path=folder_path,
                        message=(
                            "같은 폴더 경로가 다른 Pixiv ID로 이미 "
                            "등록되어 있습니다. 스캔에서 제외합니다."
                        ),
                    )
                )
                can_scan = False

        if pixiv_id in existing_by_pixiv_id:
            registered_pixiv_ids.add(pixiv_id)

        return {
            "can_scan": can_scan,
            "log_rows": log_rows,
        }

    def _build_existing_pixiv_id_map(
        self,
        artists: list[dict],
    ) -> dict[str, dict]:
        result = {}

        for artist in artists:
            pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

            if not pixiv_id:
                continue

            result[pixiv_id] = artist

        return result

    def _build_existing_folder_path_map(
        self,
        artists: list[dict],
    ) -> dict[str, dict]:
        result = {}

        for artist in artists:
            folder_path = str(artist.get("folder_path", "") or "").strip()

            if not folder_path:
                continue

            result[str(Path(folder_path).resolve()).casefold()] = artist

        return result

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

    def _build_validation_row(
        self,
        index: int,
        total: int,
        result: str,
        artist_name: str,
        pixiv_id: str,
        folder_path: Path,
        message: str,
    ) -> dict:
        progress = "-"

        if index > 0 and total > 0:
            progress = f"{index}/{total}"

        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "progress": progress,
            "result": result,
            "artist_id": None,
            "artist_name": artist_name or folder_path.name,
            "pixiv_id": pixiv_id or "-",
            "artwork_count": "-",
            "file_count": "-",
            "update_status": "-",
            "folder_path": str(folder_path),
            "error_message": message,
        }
