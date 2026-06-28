def build_follow_user_insert_values(
    data: dict,
    now: str,
) -> tuple:
    return (
        data["pixiv_user_id"],
        data["user_name"],
        data["profile_image_url"],
        data["comment"],
        data["artwork_count"],
        data["file_count"],
        data["pixiv_tags"],
        data["local_artist_id"],
        data["is_local_artist"],
        data["is_favorite"],
        data["is_hidden"],
        data["memo"],
        data["source_type"],
        data["last_synced_at"],
        data["sync_status"],
        data["sync_error_message"],
        data["sync_retry_count"],
        now,
        now,
    )


def build_follow_user_update_values(
    data: dict,
    follow_user_id: int,
    updated_at: str,
) -> tuple:
    return (
        data["pixiv_user_id"],
        data["user_name"],
        data["profile_image_url"],
        data["comment"],
        data["artwork_count"],
        data["file_count"],
        data["pixiv_tags"],
        data["local_artist_id"],
        data["is_local_artist"],
        data["is_favorite"],
        data["is_hidden"],
        data["memo"],
        data["source_type"],
        data["last_synced_at"],
        data["sync_status"],
        data["sync_error_message"],
        data["sync_retry_count"],
        updated_at,
        follow_user_id,
    )


def build_follow_user_batch_result(
    total_count: int,
    saved_count: int,
    updated_count: int,
    skipped_count: int,
    error_count: int,
    errors: list[dict],
) -> dict:
    return {
        "total_count": total_count,
        "saved_count": saved_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
        "errors": errors,
    }


def normalize_unique_ids(
    values: list[str],
) -> list[str]:
    normalized_values = []

    for value in values:
        normalized_value = str(value or "").strip()

        if not normalized_value:
            continue

        if normalized_value in normalized_values:
            continue

        normalized_values.append(normalized_value)

    return normalized_values
