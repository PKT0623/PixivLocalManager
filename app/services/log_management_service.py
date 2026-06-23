from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class LogFileInfo:
    file_name: str
    file_path: str
    category: str
    modified_at: str
    size_label: str
    size_bytes: int


class LogManagementService:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    LOG_DIR = BASE_DIR / "logs"
    CANDIDATE_LOG_DIRS = [
        BASE_DIR / "logs",
        BASE_DIR / "data" / "logs",
    ]

    CATEGORY_KEYWORDS = {
        "실행 로그": [
            "app",
            "run",
            "main",
            "error",
            "debug",
        ],
        "업데이트 로그": [
            "update",
            "check",
        ],
        "동기화 로그": [
            "sync",
            "pixiv",
            "follow",
            "bookmark",
        ],
    }

    def __init__(self):
        self.last_error = ""

    def list_log_files(self) -> list[LogFileInfo]:
        logs = []
        self.last_error = ""

        for log_dir in self.CANDIDATE_LOG_DIRS:
            try:
                if not log_dir.exists():
                    continue

                for file_path in log_dir.glob("*.log"):
                    if not file_path.is_file():
                        continue

                    log_info = self._try_create_log_file_info(file_path)

                    if log_info is None:
                        continue

                    logs.append(log_info)
            except OSError as error:
                self.last_error = str(error)
                continue

        return sorted(
            logs,
            key=lambda log: log.modified_at,
            reverse=True,
        )

    def read_log_file(
        self,
        file_path: str,
        max_chars: int = 20000,
    ) -> str:
        path = self._safe_log_path(file_path)

        if path is None or not path.exists():
            return "로그 파일을 찾을 수 없습니다."

        try:
            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError as error:
            return f"로그 파일을 읽지 못했습니다.\n{error}"

        if len(text) <= max_chars:
            return text

        return text[-max_chars:]

    def delete_log_file(
        self,
        file_path: str,
    ) -> bool:
        path = self._safe_log_path(file_path)
        self.last_error = ""

        if path is None or not path.exists():
            self.last_error = "로그 파일을 찾을 수 없습니다."
            return False

        try:
            path.unlink()
        except OSError as error:
            self.last_error = str(error)
            return False

        return True

    def delete_all_logs(self) -> int:
        deleted_count = 0

        for log in self.list_log_files():
            if self.delete_log_file(log.file_path):
                deleted_count += 1

        return deleted_count

    def ensure_log_dir(self) -> Path:
        self.LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        return self.LOG_DIR

    def append_app_log(
        self,
        message: str,
        error=None,
    ) -> bool:
        try:
            log_dir = self.ensure_log_dir()
            log_path = log_dir / "app.log"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines = [
                f"[{timestamp}] {message}",
            ]

            if error is not None:
                lines.append(f"error={error}")

            log_path.open(
                "a",
                encoding="utf-8",
            ).write("\n".join(lines) + "\n")
        except OSError as log_error:
            self.last_error = str(log_error)
            return False

        return True

    def _try_create_log_file_info(
        self,
        file_path: Path,
    ) -> LogFileInfo | None:
        try:
            return self._create_log_file_info(file_path)
        except OSError as error:
            self.last_error = str(error)
            return None

    def _create_log_file_info(
        self,
        file_path: Path,
    ) -> LogFileInfo:
        stat = file_path.stat()

        return LogFileInfo(
            file_name=file_path.name,
            file_path=str(file_path),
            category=self._detect_category(file_path.name),
            modified_at=self._format_timestamp(stat.st_mtime),
            size_label=self._format_bytes(stat.st_size),
            size_bytes=stat.st_size,
        )

    def _detect_category(
        self,
        file_name: str,
    ) -> str:
        lowered_name = file_name.lower()

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in lowered_name for keyword in keywords):
                return category

        return "기타 로그"

    def _safe_log_path(
        self,
        file_path: str,
    ) -> Path | None:
        try:
            path = Path(file_path).resolve()
        except OSError:
            return None

        for log_dir in self.CANDIDATE_LOG_DIRS:
            try:
                resolved_dir = log_dir.resolve()
            except OSError:
                continue

            if path == resolved_dir or resolved_dir in path.parents:
                return path

        return None

    def _format_timestamp(
        self,
        timestamp: float,
    ) -> str:
        return datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def _format_bytes(
        self,
        size_bytes: int,
    ) -> str:
        size = float(size_bytes)

        for unit in [
            "B",
            "KB",
            "MB",
            "GB",
            "TB",
        ]:
            if size < 1024:
                if unit == "B":
                    return f"{int(size)} {unit}"

                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size:.1f} PB"
