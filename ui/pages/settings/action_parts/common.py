class SettingsCommonActions:
    def mask_secret(self, value: str) -> str:
        if len(value) <= 8:
            return "*" * len(value)

        return f"{value[:4]}{'*' * 8}{value[-4:]}"

    def _format_integrity_result(
        self,
        result: dict,
    ) -> str:
        if result.get("ok"):
            return "무결성 검사 완료\n\n문제가 발견되지 않았습니다."

        lines = [
            "무결성 검사 완료",
            "",
            f"발견된 문제: {result.get('issue_count', 0)}건",
            "",
        ]

        grouped_issues = {}

        for issue in result.get("issues", []):
            issue_type = issue.get("type", "기타")
            grouped_issues.setdefault(issue_type, []).append(issue)

        for issue_type, issues in grouped_issues.items():
            lines.append(f"[{issue_type}]")

            for issue in issues:
                lines.append(
                    "- "
                    f"{issue.get('artist_name', '-')} "
                    f"(ID: {issue.get('artist_id', '-')}, "
                    f"Pixiv: {issue.get('pixiv_id', '-')})"
                )
                lines.append(f"  {issue.get('detail', '')}")

            lines.append("")

        return "\n".join(lines)

    def _read_int(
        self,
        value: str,
        default: int,
    ) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def set_status(self, message: str, error: bool = False):
        self.page.status_label.setText(message)

        if error:
            self.page.status_label.setStyleSheet("color: #dc3545;")
            return

        self.page.status_label.setStyleSheet("color: #198754;")
