from app.database.connection import get_connection
from app.database.migrations import run_migrations
from app.database.table_definitions import (
    CREATE_APP_SETTINGS_TABLE_SQL,
    CREATE_ARTISTS_TABLE_SQL,
)


def initialize_database() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(CREATE_ARTISTS_TABLE_SQL)
        run_migrations(cursor)

        cursor.execute(CREATE_APP_SETTINGS_TABLE_SQL)

        conn.commit()
