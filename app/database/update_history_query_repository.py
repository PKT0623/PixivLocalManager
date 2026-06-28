from datetime import datetime

from app.database.connection import get_connection


def get_update_histories_by_artist_id(
    artist_id: int,
    limit: int = 50,
) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM artist_update_history
            WHERE artist_id = ?
            ORDER BY checked_at DESC, id DESC
            LIMIT ?
            """,
            (
                artist_id,
                limit,
            ),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]


def get_update_histories_by_artist_ids(
    artist_ids: list[int],
    limit_per_artist: int = 20,
) -> dict[int, list[dict]]:
    normalized_artist_ids = []

    for artist_id in artist_ids:
        try:
            normalized_artist_id = int(artist_id)
        except (TypeError, ValueError):
            continue

        if normalized_artist_id in normalized_artist_ids:
            continue

        normalized_artist_ids.append(normalized_artist_id)

    if not normalized_artist_ids:
        return {}

    placeholders = ", ".join("?" for _ in normalized_artist_ids)

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT *
            FROM (
                SELECT
                    history.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY artist_id
                        ORDER BY checked_at DESC, id DESC
                    ) AS row_number
                FROM artist_update_history AS history
                WHERE artist_id IN ({placeholders})
            )
            WHERE row_number <= ?
            ORDER BY checked_at DESC, id DESC
            """,
            (*normalized_artist_ids, limit_per_artist),
        )

        rows = cursor.fetchall()

    histories_by_artist_id = {
        artist_id: []
        for artist_id in normalized_artist_ids
    }

    for row in rows:
        history = dict(row)
        history.pop("row_number", None)

        try:
            artist_id = int(history.get("artist_id"))
        except (TypeError, ValueError):
            continue

        histories_by_artist_id.setdefault(artist_id, []).append(history)

    return histories_by_artist_id


def get_recent_update_histories(
    limit: int = 100,
) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM artist_update_history
            ORDER BY checked_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]


def get_today_update_histories() -> list[dict]:
    today = datetime.now().date().isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM artist_update_history
            WHERE date(checked_at) = ?
            ORDER BY checked_at DESC, id DESC
            """,
            (today,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]


def get_recent_error_update_histories(
    limit: int = 20,
) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM artist_update_history
            WHERE result_status = 'error'
               OR result_label = '확인 실패'
               OR action = 'error'
            ORDER BY checked_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]


def get_latest_update_history_per_artist() -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT history.*
            FROM artist_update_history AS history
            INNER JOIN (
                SELECT artist_id, MAX(checked_at) AS latest_checked_at
                FROM artist_update_history
                GROUP BY artist_id
            ) AS latest
                ON history.artist_id = latest.artist_id
               AND history.checked_at = latest.latest_checked_at
            ORDER BY history.checked_at DESC, history.id DESC
            """
        )

        rows = cursor.fetchall()

        latest_by_artist = {}

        for row in rows:
            history = dict(row)
            artist_id = history.get("artist_id")

            if artist_id in latest_by_artist:
                continue

            latest_by_artist[artist_id] = history

        return list(latest_by_artist.values())


def get_latest_update_history_by_artist_id(
    artist_id: int,
) -> dict | None:
    rows = get_update_histories_by_artist_id(
        artist_id=artist_id,
        limit=1,
    )

    if not rows:
        return None

    return rows[0]


def delete_update_histories_by_artist_id(
    artist_id: int,
) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM artist_update_history
            WHERE artist_id = ?
            """,
            (artist_id,),
        )

        conn.commit()
