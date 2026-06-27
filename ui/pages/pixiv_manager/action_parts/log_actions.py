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

        read_count = result.get("total_count", 0)
        new_count = result.get("new_count", 0)
        duplicate_in_file_count = result.get("duplicate_in_file_count", 0)
        duplicate_existing_count = result.get(
            "duplicate_existing_count",
            0,
        )
        saved_count = save_result.get("saved_count", 0)
        error_count = save_result.get("error_count", 0)

        return (
            f"{target_label} {file_type.upper()} 가져오기 {action_label}: "
            f"읽음 {read_count}개 / "
            f"신규 {new_count}개 / "
            f"파일 중복 {duplicate_in_file_count}개 / "
            f"기존 중복 {duplicate_existing_count}개 / "
            f"저장 {saved_count}개 / "
            f"오류 {error_count}개"
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
