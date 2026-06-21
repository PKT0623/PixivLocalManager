import csv
from datetime import datetime
from pathlib import Path


class NonArtworkFileExporter:
    TXT_GROUP_ORDER = [
        "unsupported_extension",
        "artwork_id_not_found",
        "empty_file",
        "scan_error",
    ]

    TXT_GROUP_TITLES = {
        "unsupported_extension": "지원하지 않는 확장자",
        "artwork_id_not_found": "작품 ID 추출 실패",
        "empty_file": "0바이트 파일",
        "scan_error": "파일 확인 오류",
    }

    CSV_FIELDS = [
        "reason",
        "reason_label",
        "extension",
        "file_name",
        "file_path",
        "folder_path",
        "size_bytes",
    ]

    def export_txt(
        self,
        records: list[dict],
        output_path: str,
    ) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        grouped_records = self._group_records(records)

        lines = [
            "스캔 비작품 파일 목록",
            f"생성일시: {self._now_text()}",
            f"총 개수: {len(records)}",
            "",
        ]

        for reason in self.TXT_GROUP_ORDER:
            reason_records = grouped_records.get(reason, [])

            if not reason_records:
                continue

            title = self.TXT_GROUP_TITLES.get(reason, reason)

            lines.append(f"[{title}]")
            lines.append(f"개수: {len(reason_records)}")

            for record in reason_records:
                extension = record.get("extension", "")
                file_path = record.get("file_path", "")

                lines.append(f"{extension} | {file_path}")

            lines.append("")

        extra_reasons = [
            reason
            for reason in grouped_records.keys()
            if reason not in self.TXT_GROUP_ORDER
        ]

        for reason in sorted(extra_reasons):
            reason_records = grouped_records.get(reason, [])

            if not reason_records:
                continue

            lines.append(f"[{reason}]")
            lines.append(f"개수: {len(reason_records)}")

            for record in reason_records:
                extension = record.get("extension", "")
                file_path = record.get("file_path", "")

                lines.append(f"{extension} | {file_path}")

            lines.append("")

        path.write_text(
            "\n".join(lines),
            encoding="utf-8-sig",
        )

        return str(path)

    def export_csv(
        self,
        records: list[dict],
        output_path: str,
    ) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.CSV_FIELDS,
                extrasaction="ignore",
            )
            writer.writeheader()

            for record in records:
                writer.writerow(record)

        return str(path)

    def _group_records(
        self,
        records: list[dict],
    ) -> dict[str, list[dict]]:
        grouped_records: dict[str, list[dict]] = {}

        for record in records:
            reason = str(record.get("reason", "") or "unknown")

            if reason not in grouped_records:
                grouped_records[reason] = []

            grouped_records[reason].append(record)

        return grouped_records

    def _now_text(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
