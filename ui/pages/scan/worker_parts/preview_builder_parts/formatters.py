class PreviewFormatterMixin:
    def _split_artwork_ids(
        self,
        value: str,
    ) -> list[str]:
        return [
            item.strip()
            for item in str(value or "").split(",")
            if item.strip()
        ]

    def _format_overflow_count(
        self,
        total_count: int,
        display_limit: int,
    ) -> str:
        remain_count = int(total_count or 0) - int(display_limit or 0)

        if remain_count <= 0:
            return ""

        return f" 외 {remain_count}개"

    def _is_value_changed(
        self,
        old_value,
        new_value,
    ) -> bool:
        return str(old_value or "") != str(new_value or "")

    def _format_text_change_value(
        self,
        value,
    ) -> str:
        value = str(value or "").strip()

        if not value:
            return "-"

        return value

    def _format_number_change_value(
        self,
        value,
    ) -> str:
        try:
            return str(int(value or 0))
        except (TypeError, ValueError):
            return "0"

    def _format_size_change_value(
        self,
        value,
    ) -> str:
        try:
            size = int(value or 0)
        except (TypeError, ValueError):
            size = 0

        if size >= 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"

        if size >= 1024:
            return f"{size / 1024:.2f} KB"

        return f"{size} B"
