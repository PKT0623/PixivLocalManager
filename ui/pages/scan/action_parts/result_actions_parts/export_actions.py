import csv
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from app.services.scan import NonArtworkFileExporter


class ScanResultExportActionsMixin:
    def export_failed_items_csv(self):
        failed_rows = self.page.log_table.get_failed_rows()

        if not failed_rows:
            self.page.log_table.add_info_log(
                "CSV로 저장할 실패 항목이 없습니다."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.page,
            "실패 항목 CSV 저장",
            "scan_failed_items.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            self._write_rows_csv(file_path, failed_rows)
        except Exception as error:
            self.page.log_table.add_info_log(
                f"실패 항목 CSV 저장 실패: {error}"
            )
            return

        self.page.log_table.add_info_log(
            f"실패 항목 CSV 저장 완료: {file_path}"
        )

    def export_all_scan_results_csv(self):
        rows = list(self.page.log_table.all_rows)

        if not rows:
            self.page.log_table.add_info_log("CSV로 저장할 결과가 없습니다.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.page,
            "스캔 결과 CSV 저장",
            "scan_results.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            self._write_rows_csv(file_path, rows)
        except Exception as error:
            self.page.log_table.add_info_log(
                f"스캔 결과 CSV 저장 실패: {error}"
            )
            return

        self.page.log_table.add_info_log(
            f"스캔 결과 CSV 저장 완료: {file_path}"
        )

    def export_preview_results_csv(self):
        rows = self.page.preview_table.get_all_preview_rows()

        if not rows:
            self.page.log_table.add_info_log(
                "CSV로 저장할 미리보기 결과가 없습니다."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.page,
            "미리보기 결과 CSV 저장",
            "scan_preview_results.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            self._write_preview_rows_csv(file_path, rows)
        except Exception as error:
            self.page.log_table.add_info_log(
                f"미리보기 결과 CSV 저장 실패: {error}"
            )
            return

        self.page.log_table.add_info_log(
            f"미리보기 결과 CSV 저장 완료: {file_path}"
        )

    def export_non_artwork_files_txt(self):
        records = self._collect_non_artwork_files_from_preview()

        if not records:
            self.page.log_table.add_info_log(
                "TXT로 저장할 비작품 파일 목록이 없습니다."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.page,
            "비작품 파일 TXT 저장",
            "scan_non_artwork_files.txt",
            "Text Files (*.txt)",
        )

        if not file_path:
            return

        try:
            exporter = NonArtworkFileExporter()
            saved_path = exporter.export_txt(records, file_path)
        except Exception as error:
            self.page.log_table.add_info_log(
                f"비작품 파일 TXT 저장 실패: {error}"
            )
            return

        self.page.log_table.add_info_log(
            f"비작품 파일 TXT 저장 완료: {saved_path}"
        )

    def export_non_artwork_files_csv(self):
        records = self._collect_non_artwork_files_from_preview()

        if not records:
            self.page.log_table.add_info_log(
                "CSV로 저장할 비작품 파일 목록이 없습니다."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.page,
            "비작품 파일 CSV 저장",
            "scan_non_artwork_files.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            exporter = NonArtworkFileExporter()
            saved_path = exporter.export_csv(records, file_path)
        except Exception as error:
            self.page.log_table.add_info_log(
                f"비작품 파일 CSV 저장 실패: {error}"
            )
            return

        self.page.log_table.add_info_log(
            f"비작품 파일 CSV 저장 완료: {saved_path}"
        )

    def _write_rows_csv(
        self,
        file_path: str | Path,
        rows: list[dict],
    ):
        fieldnames = [
            "time",
            "progress",
            "result",
            "artist_name",
            "pixiv_id",
            "artwork_count",
            "file_count",
            "update_status",
            "folder_path",
            "error_message",
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )
            writer.writeheader()

            for row in rows:
                writer.writerow(
                    {
                        "time": row.get("time", "-"),
                        "progress": row.get("progress", "-"),
                        "result": row.get("result", "-"),
                        "artist_name": row.get("artist_name", "-"),
                        "pixiv_id": row.get("pixiv_id", "-"),
                        "artwork_count": row.get("artwork_count", "-"),
                        "file_count": row.get("file_count", "-"),
                        "update_status": row.get("update_status", "-"),
                        "folder_path": row.get("folder_path", "-"),
                        "error_message": row.get("error_message", "-"),
                    }
                )

    def _write_preview_rows_csv(
        self,
        file_path: str | Path,
        rows: list[dict],
    ):
        fieldnames = [
            "selected",
            "excluded",
            "preview_result",
            "artist_name",
            "pixiv_id",
            "artwork_count",
            "file_count",
            "folder_path",
            "message",
            "non_artwork_summary_text",
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )
            writer.writeheader()

            for row in rows:
                writer.writerow(
                    {
                        "selected": row.get("selected", "0"),
                        "excluded": row.get("is_excluded", "0"),
                        "preview_result": row.get("preview_result", "-"),
                        "artist_name": row.get("artist_name", "-"),
                        "pixiv_id": row.get("pixiv_id", "-"),
                        "artwork_count": row.get("artwork_count", "-"),
                        "file_count": row.get("file_count", "-"),
                        "folder_path": row.get("folder_path", "-"),
                        "message": row.get("message", "-"),
                        "non_artwork_summary_text": row.get(
                            "non_artwork_summary_text",
                            "-",
                        ),
                    }
                )
