from PySide6.QtWidgets import QFileDialog

from app.services.pixiv_update_service import PixivUpdateService


class SettingsPixivActions:
    def select_pixiv_root_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self.page,
            "기본 Pixiv 폴더 선택",
            self.page.folder_section.pixiv_root_input.text().strip(),
        )

        if not folder_path:
            return

        self.page.folder_section.pixiv_root_input.setText(folder_path)
        self.set_status("기본 Pixiv 폴더를 선택했습니다. 저장 버튼을 눌러 반영하세요.")

    def save_pixiv_root_folder(self):
        folder_path = self.page.folder_section.pixiv_root_input.text().strip()

        if not folder_path:
            self.set_status("저장할 Pixiv 폴더가 없습니다.", error=True)
            return

        try:
            self.page.settings_service.set_setting(
                "pixiv_root_folder",
                folder_path,
            )
        except Exception as error:
            self.set_status(f"기본 Pixiv 폴더 저장 실패: {error}", error=True)
            return

        self.refresh_environment_info()
        self.set_status("기본 Pixiv 폴더가 저장되었습니다.")

    def save_scan_image_extensions(self):
        extensions = self.page.folder_section.get_scan_image_extensions()

        if not extensions:
            self.set_status(
                "작품 파일 확장자를 최소 1개 이상 선택하세요.",
                error=True,
            )
            return

        try:
            self.page.settings_service.set_scan_image_extensions(extensions)
        except Exception as error:
            self.set_status(f"작품 파일 확장자 저장 실패: {error}", error=True)
            return

        self._load_scan_image_extensions()
        self.set_status("작품 파일 확장자 설정이 저장되었습니다.")

    def reset_scan_image_extensions(self):
        try:
            self.page.settings_service.reset_scan_image_extensions()
        except Exception as error:
            self.set_status(f"작품 파일 확장자 기본값 복원 실패: {error}", error=True)
            return

        self._load_scan_image_extensions()
        self.set_status("작품 파일 확장자 기본값을 복원했습니다.")

    def save_phpsessid(self):
        phpsessid = self.page.pixiv_section.phpsessid_input.text().strip()

        if not phpsessid:
            self.set_status("저장할 PHPSESSID가 없습니다.", error=True)
            return

        try:
            self.page.settings_service.set_setting(
                "pixiv_phpsessid",
                phpsessid,
            )
        except Exception as error:
            self.set_status(f"PHPSESSID 저장 실패: {error}", error=True)
            return

        self.page.pixiv_section.phpsessid_status_label.setText(
            f"저장됨: {self.mask_secret(phpsessid)}"
        )
        self.page.pixiv_section.session_status_label.setText(
            "세션 상태: 미확인"
        )
        self.set_status("Pixiv PHPSESSID가 저장되었습니다.")

    def test_phpsessid(self):
        phpsessid = self.page.pixiv_section.phpsessid_input.text().strip()

        if not phpsessid:
            phpsessid = self.page.settings_service.get_setting(
                "pixiv_phpsessid"
            )

        if not phpsessid:
            self.page.pixiv_section.session_status_label.setText(
                "세션 상태: 만료"
            )
            self.set_status("테스트할 PHPSESSID가 없습니다.", error=True)
            return

        self.page.pixiv_section.test_phpsessid_button.setEnabled(False)
        self.set_status("PHPSESSID 테스트 중...")

        try:
            pixiv_service = PixivUpdateService.from_settings(
                self.page.settings_service
            )
            result = pixiv_service.test_phpsessid(phpsessid)
        except Exception as error:
            self.page.pixiv_section.session_status_label.setText(
                "세션 상태: 오류"
            )
            self.set_status(f"PHPSESSID 테스트 실패: {error}", error=True)
            self.page.pixiv_section.test_phpsessid_button.setEnabled(True)
            return

        self.page.pixiv_section.test_phpsessid_button.setEnabled(True)

        session_status = self.pixiv_session_service.get_status_from_test_result(
            result
        )
        self.page.pixiv_section.session_status_label.setText(
            f"세션 상태: {session_status}"
        )

        if result.get("success"):
            self.set_status("PHPSESSID가 유효합니다.")
            return

        self.set_status(
            f"PHPSESSID 테스트 실패: {result.get('message')}",
            error=True,
        )
