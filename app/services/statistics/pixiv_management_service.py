from app.database.connection import get_connection


class StatisticsPixivManagementService:
    def get_pixiv_management_statistics(self) -> dict:
        return {
            "follow_count": self._get_table_count("follow_users"),
            "bookmark_count": self._get_table_count("bookmark_artworks"),
        }

    def _get_table_count(
        self,
        table_name: str,
    ) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            except Exception:
                return 0

            row = cursor.fetchone()

            if row is None:
                return 0

            return int(row[0] or 0)

