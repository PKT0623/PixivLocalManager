class PixivSessionService:
    COOKIE_MISSING = "COOKIE_MISSING"
    COOKIE_EXPIRED = "COOKIE_EXPIRED"

    def get_status_from_test_result(
        self,
        result: dict,
    ) -> str:
        if result.get("success"):
            return "정상"

        reason = result.get("reason")

        if reason in (
            self.COOKIE_EXPIRED,
            self.COOKIE_MISSING,
        ):
            return "만료"

        return "오류"
