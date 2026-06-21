from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

from app.database import ArtistUpdateHistoryRepository

from ...utils import (
    format_datetime,
    parse_id_text,
    status_label,
    to_int,
)


class ArtistUpdateHistoryActions:
    UPDATE_HISTORY_LIMIT = 20

    def set_update_history_table_data(
        self,
        artist_id,
    ):
        section = self.page.info_section
        table = section.update_history_table

        table.setRowCount(0)
        section.update_history_label.setText("업데이트 이력")
        section.update_history_summary_label.setText("최근 누락 변화: -")

        if artist_id is None:
            return

        histories = self._get_update_history_repo().get_by_artist_id_with_comparison(
            artist_id=artist_id,
            limit=self.UPDATE_HISTORY_LIMIT,
        )

        section.update_history_label.setText(
            f"업데이트 이력 ({len(histories)}건)"
        )

        if not histories:
            return

        self._set_update_history_summary(histories[0])

        for history in histories:
            self._add_update_history_row(history)

    def _add_update_history_row(
        self,
        history: dict,
    ):
        table = self.page.info_section.update_history_table

        row = table.rowCount()
        table.insertRow(row)

        values = [
            format_datetime(history.get("checked_at")),
            self._history_result_label(history),
            str(to_int(history.get("local_count", 0))),
            str(to_int(history.get("pixiv_count", 0))),
            str(to_int(history.get("missing_count", 0))),
            self._missing_delta_text(history),
            self._changed_ids_summary_text(history),
            self._history_detail_text(history),
        ]

        for column, value in enumerate(values):
            item = self._create_history_item(value)

            if column in (2, 3, 4, 5, 6):
                item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row, column, item)

    def _set_update_history_summary(
        self,
        latest_history: dict,
    ):
        summary_label = self.page.info_section.update_history_summary_label

        if not latest_history.get("has_previous"):
            summary_label.setText("최근 누락 변화: 비교 이력 없음")
            return

        delta = to_int(latest_history.get("missing_delta", 0))

        if delta > 0:
            summary_label.setText(f"최근 누락 증가: +{delta}개")
            return

        if delta < 0:
            summary_label.setText(f"최근 누락 감소: {delta}개")
            return

        summary_label.setText("최근 누락 변화: 변화 없음")

    def _history_result_label(
        self,
        history: dict,
    ) -> str:
        result_label = str(history.get("result_label", "") or "").strip()

        if result_label:
            return result_label

        return status_label(history.get("result_status"))

    def _missing_delta_text(
        self,
        history: dict,
    ) -> str:
        if not history.get("has_previous"):
            return "-"

        delta = to_int(history.get("missing_delta", 0))

        if delta > 0:
            return f"+{delta} 증가"

        if delta < 0:
            return f"{delta} 감소"

        return "변화 없음"

    def _changed_ids_summary_text(
        self,
        history: dict,
    ) -> str:
        if not history.get("has_previous"):
            return "-"

        new_count = to_int(history.get("new_missing_count", 0))
        resolved_count = to_int(history.get("resolved_missing_count", 0))

        return f"신규 {new_count} / 해결 {resolved_count}"

    def _history_detail_text(
        self,
        history: dict,
    ) -> str:
        error_message = str(history.get("error_message", "") or "").strip()
        error_reason = str(history.get("error_reason", "") or "").strip()

        if error_message and error_reason:
            return f"{error_reason}: {error_message}"

        if error_message:
            return error_message

        if error_reason:
            return error_reason

        new_missing_ids = parse_id_text(history.get("new_missing_ids", ""))
        resolved_missing_ids = parse_id_text(
            history.get("resolved_missing_ids", "")
        )

        detail_parts = []

        if new_missing_ids:
            detail_parts.append(
                "신규 누락: " + ", ".join(new_missing_ids[:10])
            )

        if resolved_missing_ids:
            detail_parts.append(
                "해결됨: " + ", ".join(resolved_missing_ids[:10])
            )

        return " / ".join(detail_parts)

    def _create_history_item(
        self,
        text: str,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text or ""))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        return item

    def _get_update_history_repo(self) -> ArtistUpdateHistoryRepository:
        if not hasattr(self, "update_history_repo"):
            self.update_history_repo = ArtistUpdateHistoryRepository()

        return self.update_history_repo
