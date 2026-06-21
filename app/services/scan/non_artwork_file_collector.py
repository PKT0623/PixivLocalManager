from dataclasses import dataclass
from pathlib import Path


@dataclass
class NonArtworkFile:
    reason: str
    reason_label: str
    extension: str
    file_name: str
    file_path: str
    folder_path: str
    size_bytes: int = 0


class NonArtworkFileCollector:
    REASON_UNSUPPORTED_EXTENSION = "unsupported_extension"
    REASON_ARTWORK_ID_NOT_FOUND = "artwork_id_not_found"
    REASON_EMPTY_FILE = "empty_file"
    REASON_SCAN_ERROR = "scan_error"

    REASON_LABELS = {
        REASON_UNSUPPORTED_EXTENSION: "지원하지 않는 확장자",
        REASON_ARTWORK_ID_NOT_FOUND: "작품 ID 추출 실패",
        REASON_EMPTY_FILE: "0바이트 파일",
        REASON_SCAN_ERROR: "파일 확인 오류",
    }

    def build_record(
        self,
        file_path: Path,
        folder_path: Path,
        reason: str,
        size_bytes: int = 0,
    ) -> dict:
        extension = file_path.suffix.lower()

        if not extension:
            extension = "(없음)"

        record = NonArtworkFile(
            reason=reason,
            reason_label=self.REASON_LABELS.get(reason, reason),
            extension=extension,
            file_name=file_path.name,
            file_path=str(file_path),
            folder_path=str(folder_path),
            size_bytes=size_bytes,
        )

        return {
            "reason": record.reason,
            "reason_label": record.reason_label,
            "extension": record.extension,
            "file_name": record.file_name,
            "file_path": record.file_path,
            "folder_path": record.folder_path,
            "size_bytes": record.size_bytes,
        }

    def summarize(
        self,
        records: list[dict],
    ) -> dict:
        summary = {
            self.REASON_UNSUPPORTED_EXTENSION: 0,
            self.REASON_ARTWORK_ID_NOT_FOUND: 0,
            self.REASON_EMPTY_FILE: 0,
            self.REASON_SCAN_ERROR: 0,
            "total": len(records),
        }

        for record in records:
            reason = record.get("reason")

            if reason not in summary:
                summary[reason] = 0

            summary[reason] += 1

        return summary

    def format_summary_text(
        self,
        summary: dict,
    ) -> str:
        total = int(summary.get("total", 0) or 0)

        if total <= 0:
            return "비작품 파일 없음"

        parts = []

        for reason in [
            self.REASON_UNSUPPORTED_EXTENSION,
            self.REASON_ARTWORK_ID_NOT_FOUND,
            self.REASON_EMPTY_FILE,
            self.REASON_SCAN_ERROR,
        ]:
            count = int(summary.get(reason, 0) or 0)

            if count <= 0:
                continue

            parts.append(
                f"{self.REASON_LABELS.get(reason, reason)} {count}개"
            )

        if not parts:
            return f"비작품 파일 {total}개"

        return f"비작품 파일 {total}개 - " + " / ".join(parts)
