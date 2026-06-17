from app.database.connection import get_connection
from app.models import AppSetting


class AppSettingRepository:

    def set(self, key: str, value: str) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO app_settings (
                    key,
                    value
                )
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value
                """,
                (
                    key,
                    str(value),
                ),
            )

            conn.commit()

    def get(self, key: str) -> AppSetting | None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM app_settings WHERE key = ?",
                (key,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return AppSetting(**dict(row))

    def get_all(self) -> list[AppSetting]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM app_settings ORDER BY key"
            )

            rows = cursor.fetchall()

            return [
                AppSetting(**dict(row))
                for row in rows
            ]

    def delete(self, key: str) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM app_settings WHERE key = ?",
                (key,),
            )

            conn.commit()

    def delete_all(self) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM app_settings")

            conn.commit()
