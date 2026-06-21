import csv
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QApplication


class UpdateCheckUtilityActions:
    def test_phpsessid(self):
        phpsessid = self.settings_service.get_setting("pixiv_phpsessid")

        if not phpsessid:
            self.page.status_label.setText(
                "PHPSESSID가 설정되어 있지 않습니다."
            )
            return

        self.page.test_phpsessid_button.setEnabled(False)
        self.page.status_label.setText("PHPSESSID 연결 테스트 중...")

        result = self.pixiv_update_service.test_phpsessid(phpsessid)

        if result.get("success"):
            self.page.status_label.setText(
                "PHPSESSID 연결 테스트에 성공했습니다."
            )
        else:
            self.page.status_label.setText(
                f"PHPSESSID 연결 테스트 실패: {result.get('message')}"
            )

        self.page.test_phpsessid_button.setEnabled(True)

    def export_log_csv(self):
        if self.page.log_table.rowCount() == 0:
            self.page.status_label.setText("저장할 결과 로그가 없습니다.")
            return

        export_dir = Path("exports") / "update_logs"
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = export_dir / f"update_check_log_{timestamp}.csv"

        headers, rows = self.page.log_table.get_csv_data()

        with file_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

        self.page.status_label.setText(
            f"CSV 저장 완료: {file_path}"
        )

    def update_log_action_buttons(self):
        if self._is_log_action_locked():
            self._set_log_action_buttons_enabled(False)
            return

        selected_artist_ids = self.page.log_table.get_selected_artist_ids()
        missing_artist_ids = self.page.log_table.get_missing_artist_ids()
        error_artist_ids = self.page.log_table.get_error_artist_ids()
        download_rows = self.page.log_table.get_download_candidate_rows()
        has_logs = self.page.log_table.rowCount() > 0

        has_selected_artist = bool(selected_artist_ids)
        has_single_selected_artist = len(selected_artist_ids) == 1

        self.page.open_log_artist_detail_button.setEnabled(
            has_single_selected_artist
        )
        self.page.open_log_artist_list_button.setEnabled(
            has_selected_artist
        )
        self.page.rescan_selected_log_button.setEnabled(
            has_selected_artist
        )
        self.page.rescan_missing_log_button.setEnabled(
            bool(missing_artist_ids)
        )
        self.page.rescan_error_log_button.setEnabled(
            bool(error_artist_ids)
        )
        self.page.export_download_txt_button.setEnabled(
            bool(download_rows)
        )
        self.page.export_download_csv_button.setEnabled(
            bool(download_rows)
        )
        self.page.export_csv_button.setEnabled(has_logs)

    def open_log_artist_detail_by_id(
        self,
        artist_id: int,
    ):
        if self._is_log_action_locked():
            return

        self.page.artist_detail_requested.emit(artist_id)

    def open_selected_log_artist_detail(self):
        if self._is_log_action_locked():
            return

        artist_ids = self.page.log_table.get_selected_artist_ids()

        if not artist_ids:
            self.page.status_label.setText("상세로 열 작가를 선택하세요.")
            return

        self.page.artist_detail_requested.emit(artist_ids[0])

    def open_selected_log_artist_list(self):
        if self._is_log_action_locked():
            return

        artist_ids = self.page.log_table.get_selected_artist_ids()

        if not artist_ids:
            self.page.status_label.setText("목록에서 볼 작가를 선택하세요.")
            return

        self.page.artist_list_requested.emit(artist_ids)

    def rescan_selected_log_artists(self):
        if self._is_log_action_locked():
            return

        artist_ids = self.page.log_table.get_selected_artist_ids()

        if not artist_ids:
            self.page.status_label.setText("재스캔할 작가를 선택하세요.")
            return

        self._rescan_log_artist_ids(
            artist_ids=artist_ids,
            label="선택 작가",
        )

    def rescan_missing_log_artists(self):
        if self._is_log_action_locked():
            return

        artist_ids = self.page.log_table.get_missing_artist_ids()

        if not artist_ids:
            self.page.status_label.setText("재스캔할 누락 작가가 없습니다.")
            return

        self._rescan_log_artist_ids(
            artist_ids=artist_ids,
            label="누락 작가",
        )

    def rescan_error_log_artists(self):
        if self._is_log_action_locked():
            return

        artist_ids = self.page.log_table.get_error_artist_ids()

        if not artist_ids:
            self.page.status_label.setText("재스캔할 오류 작가가 없습니다.")
            return

        self._rescan_log_artist_ids(
            artist_ids=artist_ids,
            label="오류 작가",
        )

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

    def _rescan_log_artist_ids(
        self,
        artist_ids: list[int],
        label: str,
    ):
        scan_page = self._get_scan_page()

        if scan_page is None:
            self.page.status_label.setText(
                "폴더 스캔 페이지를 찾을 수 없습니다."
            )
            return

        folder_paths = self._get_artist_folder_paths(artist_ids)

        if not folder_paths:
            self.page.status_label.setText(
                f"{label} 재스캔 대상 폴더가 없습니다."
            )
            return

        root_folder = self._resolve_rescan_root_folder(folder_paths)

        scan_page.folder_section.folder_path_input.setText(root_folder)
        scan_page.actions.clear_resume_state()
        scan_page.log_table.add_info_log(
            f"업데이트 확인 결과 기반 재스캔 대상: {len(folder_paths)}개"
        )
        scan_page.actions._start_worker(
            folder_path=root_folder,
            target_folder_paths=folder_paths,
            clear_log=False,
            preview_mode=False,
            resume_payload=None,
        )

        self.page.status_label.setText(
            f"{label} 재스캔을 시작했습니다: {len(folder_paths)}개"
        )

    def _get_scan_page(self):
        main_window = self.page.window()

        if main_window is None:
            return None

        pages = getattr(main_window, "pages", {})

        return pages.get("scan")

    def _get_artist_folder_paths(
        self,
        artist_ids: list[int],
    ) -> list[str]:
        folder_paths = []
        seen_paths = set()

        for artist_id in artist_ids:
            artist = self._get_artist(artist_id)

            if not artist:
                continue

            folder_path = str(artist.get("folder_path", "") or "").strip()

            if not folder_path:
                continue

            if folder_path in seen_paths:
                continue

            seen_paths.add(folder_path)
            folder_paths.append(folder_path)

        return folder_paths

    def _get_artist(
        self,
        artist_id: int,
    ):
        service = self.page.artist_service

        if hasattr(service, "get_artist"):
            return service.get_artist(artist_id)

        if hasattr(service, "get_by_id"):
            return service.get_by_id(artist_id)

        if hasattr(service, "repo"):
            return service.repo.get_by_id(artist_id)

        return None

    def _resolve_rescan_root_folder(
        self,
        folder_paths: list[str],
    ) -> str:
        if not folder_paths:
            return ""

        if len(folder_paths) == 1:
            return str(Path(folder_paths[0]).parent)

        try:
            import os

            return os.path.commonpath(
                [
                    str(Path(folder_path).parent)
                    for folder_path in folder_paths
                ]
            )
        except Exception:
            return str(Path(folder_paths[0]).parent)

    def _is_log_action_locked(self) -> bool:
        if self._is_worker_running():
            return True

        if getattr(self, "is_paused", False):
            return True

        return False

    def _set_log_action_buttons_enabled(
        self,
        enabled: bool,
    ):
        buttons = [
            self.page.open_log_artist_detail_button,
            self.page.open_log_artist_list_button,
            self.page.rescan_selected_log_button,
            self.page.rescan_missing_log_button,
            self.page.rescan_error_log_button,
            self.page.export_download_txt_button,
            self.page.export_download_csv_button,
        ]

        for button in buttons:
            button.setEnabled(enabled)
