from datetime import datetime


class PixivManagerLogActions:
    def clear_logs(self):
        self.page.log_table.clear_logs()
        self.page.status_label.setText("결과 로그를 초기화했습니다.")

    def _format_file_import_finished_message(
        self,
        target_label: str,
        file_type: str,
        result: dict,
        save_result: dict,
        cancelled: bool,
    ) -> str:
        action_label = "취소" if cancelled else "완료"

        return (
            f"{target_label} {file_type.upper()} 가져오기 {action_label}: "
            f"신규 {result.get('new_count', 0)}개 / "
            f"저장 {save_result.get('saved_count', 0)}개 / "
            f"오류 {save_result.get('error_count', 0)}개"
        )

    def _add_log(
        self,
        target: str,
        result: str,
        message: str,
        new_count: int,
        duplicate_in_file_count: int,
        duplicate_existing_count: int,
        error_count: int,
    ):
        self.page.log_table.add_log_row(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "target": target,
                "result": result,
                "message": message,
                "new_count": new_count,
                "duplicate_in_file_count": duplicate_in_file_count,
                "duplicate_existing_count": duplicate_existing_count,
                "error_count": error_count,
            }
        )

    def _get_target_label(
        self,
        target_type: str,
    ) -> str:
        if target_type == "bookmark":
            return "북마크"

        return "팔로우"

    def _get_pixiv_error_result_label(
        self,
        reason: str,
    ) -> str:
        if reason == "NO_SELECTION":
            return "스킵"

        if reason == "CANCELLED":
            return "취소"

        if reason in (
            "COOKIE_EXPIRED",
            "COOKIE_MISSING",
        ):
            return "세션 오류"

        if reason == "RATE_LIMIT":
            return "요청 제한"

        return "실패"
