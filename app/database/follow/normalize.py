def normalize_follow_user(follow_user: dict) -> dict:
    pixiv_user_id = str(
        follow_user.get("pixiv_user_id", "") or ""
    ).strip()

    if not pixiv_user_id:
        raise ValueError("Pixiv 유저 ID가 비어 있습니다.")

    local_artist_id = follow_user.get("local_artist_id")

    if local_artist_id in ("", 0):
        local_artist_id = None

    if local_artist_id is not None:
        local_artist_id = int(local_artist_id)

    is_local_artist = int(
        bool(follow_user.get("is_local_artist", False))
        or local_artist_id is not None
    )

    return {
        "pixiv_user_id": pixiv_user_id,
        "user_name": str(follow_user.get("user_name", "") or "").strip(),
        "profile_image_url": str(
            follow_user.get("profile_image_url", "") or ""
        ).strip(),
        "comment": str(follow_user.get("comment", "") or ""),
        "artwork_count": int(follow_user.get("artwork_count", 0) or 0),
        "file_count": int(follow_user.get("file_count", 0) or 0),
        "pixiv_tags": str(follow_user.get("pixiv_tags", "") or ""),
        "local_artist_id": local_artist_id,
        "is_local_artist": is_local_artist,
        "is_favorite": int(bool(follow_user.get("is_favorite", 0))),
        "is_hidden": int(bool(follow_user.get("is_hidden", 0))),
        "memo": str(follow_user.get("memo", "") or ""),
        "source_type": str(
            follow_user.get("source_type", "manual") or "manual"
        ),
        "last_synced_at": follow_user.get("last_synced_at"),
        "sync_status": str(
            follow_user.get("sync_status", "pending") or "pending"
        ),
        "sync_error_message": str(
            follow_user.get("sync_error_message", "") or ""
        ),
        "sync_retry_count": int(
            follow_user.get("sync_retry_count", 0) or 0
        ),
    }
