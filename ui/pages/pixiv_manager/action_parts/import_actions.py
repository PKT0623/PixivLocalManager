from pathlib import Path

from PySide6.QtWidgets import QFileDialog


class PixivManagerImportActions:
    def browse_file(self):
        if self._is_worker_running():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self.page,
            "ID 목록 파일 선택",
            "",
            "ID 목록 파일 (*.txt *.csv);;TXT 파일 (*.txt);;CSV 파일 (*.csv)",
        )

        if not file_path:
            return

        self.page.file_path_input.setText(file_path)
        self._select_file_type_by_extension(file_path)

    def import_file(self):
        target_type = self._get_target_type()
        file_type = self._get_file_type()

        if not file_type:
            return

        self._start_import(
            target_type=target_type,
            file_type=file_type,
            import_source="file",
        )

    def import_pixiv_follow(self):
        self._start_pixiv_import("follow")

    def import_pixiv_bookmark(self):
        self._start_pixiv_import("bookmark")

    def cancel_import(self):
        if not self._is_worker_running():
            return

        if self.page.worker is None:
            return

        self.page.worker.request_cancel()
        self.page.cancel_import_button.setEnabled(False)
        self.page.status_label.setText(
            "취소 요청됨: 현재 항목 처리 후 중단합니다."
        )

        self._add_log(
            target="-",
            result="취소 요청",
            message="사용자가 가져오기 취소를 요청했습니다.",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=0,
        )

    def _start_pixiv_import(
        self,
        target_type: str,
    ):
        if self._is_worker_running():
            self.page.status_label.setText(
                "이미 가져오기가 진행 중입니다."
            )
            return

        phpsessid = self.settings_service.get_setting("pixiv_phpsessid")

        if not phpsessid:
            self._add_log(
                target=self._get_target_label(target_type),
                result="세션 오류",
                message="Pixiv PHPSESSID가 설정되어 있지 않습니다.",
                new_count=0,
                duplicate_in_file_count=0,
                duplicate_existing_count=0,
                error_count=1,
            )
            self.page.status_label.setText(
                "Pixiv PHPSESSID가 설정되어 있지 않습니다."
            )
            return

        selected_items = self._get_selected_pixiv_items(target_type)

        if not selected_items:
            self.page.status_label.setText("선택된 항목이 없습니다.")
            self._add_log(
                target=self._get_target_label(target_type),
                result="스킵",
                message="선택된 항목이 없습니다.",
                new_count=0,
                duplicate_in_file_count=0,
                duplicate_existing_count=0,
                error_count=0,
            )
            return

        self._add_log(
            target=self._get_target_label(target_type),
            result="시작",
            message=f"선택 항목 {len(selected_items)}개 메타데이터 갱신 준비 중",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=0,
        )

        self._start_import(
            target_type=target_type,
            file_type="pixiv",
            import_source="pixiv",
            phpsessid=phpsessid,
            selected_items=selected_items,
        )

    def _get_selected_pixiv_items(
        self,
        target_type: str,
    ) -> list[dict]:
        if target_type == "follow":
            selected_ids = self.page.follow_table.get_checked_ids()

            if not selected_ids:
                return []

            selected_id_set = set(selected_ids)

            return [
                item
                for item in self.follow_users
                if int(item.get("id", 0) or 0) in selected_id_set
            ]

        selected_ids = self.page.bookmark_table.get_checked_ids()

        if not selected_ids:
            return []

        selected_id_set = set(selected_ids)

        return [
            item
            for item in self.bookmark_artworks
            if int(item.get("id", 0) or 0) in selected_id_set
        ]

    def _get_file_path(self) -> str:
        file_path = self.page.file_path_input.text().strip()

        if not file_path:
            self.page.status_label.setText(
                "가져올 파일 경로를 입력하세요."
            )
            return ""

        path = Path(file_path)

        if not path.exists():
            self.page.status_label.setText(
                f"파일을 찾을 수 없습니다: {file_path}"
            )
            return ""

        return str(path)

    def _get_target_type(self) -> str:
        target_text = self.page.import_target_combo.currentText()

        if target_text == "북마크 작품":
            return "bookmark"

        return "follow"

    def _get_file_type(self) -> str:
        file_type_text = self.page.import_file_type_combo.currentText()

        if file_type_text == "TXT":
            return "txt"

        if file_type_text == "CSV":
            return "csv"

        file_path = self.page.file_path_input.text().strip()
        extension = Path(file_path).suffix.lower()

        if extension == ".txt":
            return "txt"

        if extension == ".csv":
            return "csv"

        self.page.status_label.setText(
            "파일 형식을 자동 감지할 수 없습니다. TXT 또는 CSV를 선택하세요."
        )

        return ""

    def _select_file_type_by_extension(
        self,
        file_path: str,
    ):
        extension = Path(file_path).suffix.lower()

        if extension == ".txt":
            self.page.import_file_type_combo.setCurrentText("TXT")
            return

        if extension == ".csv":
            self.page.import_file_type_combo.setCurrentText("CSV")
            return

        self.page.import_file_type_combo.setCurrentText("자동 감지")
