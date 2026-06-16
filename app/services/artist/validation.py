def validate_artist_ids(artist_ids: list[int]) -> None:
    if not artist_ids:
        raise ValueError("선택된 작가가 없습니다.")

    for artist_id in artist_ids:
        if artist_id is None:
            raise ValueError("잘못된 작가 ID가 포함되어 있습니다.")

        if int(artist_id) <= 0:
            raise ValueError("잘못된 작가 ID가 포함되어 있습니다.")
