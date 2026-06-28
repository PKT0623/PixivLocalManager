class UpdateCheckPhpsessidActionsMixin:
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
