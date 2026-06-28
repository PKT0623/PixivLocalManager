class UpdateLogTableFormatterMixin:
    def _normalize_id_list(
        self,
        value,
    ) -> list[str]:
        if value is None:
            return []

        if isinstance(value, (list, tuple, set)):
            items = value
        else:
            text = str(value).strip()

            if not text:
                return []

            items = text.replace("\n", ",").split(",")

        normalized_items = []

        for item in items:
            text = str(item).strip()

            if not text or text == "-":
                continue

            normalized_items.append(text)

        return normalized_items

    def _format_id_list(
        self,
        value,
    ) -> str:
        return ", ".join(self._normalize_id_list(value))

    def _to_int(
        self,
        value,
    ) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
