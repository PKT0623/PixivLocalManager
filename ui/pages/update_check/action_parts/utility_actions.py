import csv
from datetime import datetime
from pathlib import Path


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
