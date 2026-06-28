from pathlib import Path


class UpdateCheckRescanActionsMixin:
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
