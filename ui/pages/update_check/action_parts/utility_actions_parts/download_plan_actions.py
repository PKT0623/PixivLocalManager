import csv
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QApplication


class UpdateCheckDownloadPlanActionsMixin:
    def export_download_plan_txt(self):
        if self._is_log_action_locked():
            return

        rows = self.page.log_table.get_download_candidate_rows()

        if not rows:
            self.page.status_label.setText("저장할 다운로드 예정 목록이 없습니다.")
            return

        export_dir = Path("exports") / "download_plans"
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = export_dir / f"download_plan_{timestamp}.txt"

        lines = [
            "다운로드 예정 목록",
            f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"작가 수: {len(rows)}",
            "",
        ]

        total_count = 0

        for row in rows:
            ids = row.get("download_candidate_ids", [])
            total_count += len(ids)

            lines.append(
                f"[{row.get('artist_name', '-')}] "
                f"Pixiv ID: {row.get('pixiv_id', '-')}"
            )
            lines.append(f"누락 작품 수: {len(ids)}")

            for artwork_id in ids:
                lines.append(str(artwork_id))

            lines.append("")

        lines.insert(3, f"작품 수: {total_count}")

        file_path.write_text(
            "\n".join(lines),
            encoding="utf-8-sig",
        )

        self.page.status_label.setText(
            f"다운로드 예정 TXT 저장 완료: {file_path}"
        )

    def export_download_plan_csv(self):
        if self._is_log_action_locked():
            return

        rows = self.page.log_table.get_download_candidate_rows()

        if not rows:
            self.page.status_label.setText("저장할 다운로드 예정 목록이 없습니다.")
            return

        export_dir = Path("exports") / "download_plans"
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = export_dir / f"download_plan_{timestamp}.csv"

        with file_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "artist_id",
                    "artist_name",
                    "pixiv_id",
                    "artwork_id",
                ]
            )

            for row in rows:
                for artwork_id in row.get("download_candidate_ids", []):
                    writer.writerow(
                        [
                            row.get("artist_id", ""),
                            row.get("artist_name", "-"),
                            row.get("pixiv_id", "-"),
                            artwork_id,
                        ]
                    )

        self.page.status_label.setText(
            f"다운로드 예정 CSV 저장 완료: {file_path}"
        )

    def copy_download_plan_to_clipboard(self):
        if self._is_log_action_locked():
            return

        rows = self.page.log_table.get_download_candidate_rows()

        if not rows:
            self.page.status_label.setText("복사할 다운로드 예정 목록이 없습니다.")
            return

        lines = []

        for row in rows:
            lines.append(
                f"[{row.get('artist_name', '-')}] "
                f"Pixiv ID: {row.get('pixiv_id', '-')}"
            )

            for artwork_id in row.get("download_candidate_ids", []):
                lines.append(str(artwork_id))

            lines.append("")

        QApplication.clipboard().setText("\n".join(lines))
        self.page.status_label.setText("다운로드 예정 목록을 클립보드에 복사했습니다.")
