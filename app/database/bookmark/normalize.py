def normalize_bookmark_artwork(bookmark_artwork: dict) -> dict:
    artwork_id = str(bookmark_artwork.get("artwork_id", "") or "").strip()

    if not artwork_id:
        raise ValueError("작품 ID가 비어 있습니다.")

    local_artist_id = bookmark_artwork.get("local_artist_id")

    if local_artist_id in ("", 0):
        local_artist_id = None

    if local_artist_id is not None:
        local_artist_id = int(local_artist_id)

    is_local_artist = int(
        bool(bookmark_artwork.get("is_local_artist", False))
        or local_artist_id is not None
    )

    ai_type = int(bookmark_artwork.get("ai_type", 0) or 0)
    is_ai_generated = int(
        bool(bookmark_artwork.get("is_ai_generated", False))
        or ai_type == 2
    )

    return {
        "artwork_id": artwork_id,
        "title": str(bookmark_artwork.get("title", "") or "").strip(),
        "artist_id": str(
            bookmark_artwork.get("artist_id", "") or ""
        ).strip(),
        "artist_name": str(
            bookmark_artwork.get("artist_name", "") or ""
        ).strip(),
        "bookmark_count": int(
            bookmark_artwork.get("bookmark_count", 0) or 0
        ),
        "page_count": int(bookmark_artwork.get("page_count", 0) or 0),
        "ai_type": ai_type,
        "is_ai_generated": is_ai_generated,
        "pixiv_tags": str(bookmark_artwork.get("pixiv_tags", "") or ""),
        "local_artist_id": local_artist_id,
        "is_local_artist": is_local_artist,
        "is_favorite": int(bool(bookmark_artwork.get("is_favorite", 0))),
        "is_hidden": int(bool(bookmark_artwork.get("is_hidden", 0))),
        "memo": str(bookmark_artwork.get("memo", "") or ""),
        "source_type": str(
            bookmark_artwork.get("source_type", "manual") or "manual"
        ),
        "last_synced_at": bookmark_artwork.get("last_synced_at"),
        "sync_status": str(
            bookmark_artwork.get("sync_status", "pending") or "pending"
        ),
        "sync_error_message": str(
            bookmark_artwork.get("sync_error_message", "") or ""
        ),
        "sync_retry_count": int(
            bookmark_artwork.get("sync_retry_count", 0) or 0
        ),
    }
