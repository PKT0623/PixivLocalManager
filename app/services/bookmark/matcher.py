from app.database import ArtistRepository, BookmarkArtworkRepository


class BookmarkArtworkMatcher:
    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.bookmark_artwork_repo = BookmarkArtworkRepository()

    def match_bookmark_artwork(
        self,
        bookmark_artwork: dict,
    ) -> dict:
        artist_map = self.artist_repo.get_pixiv_id_map()

        return self._match_bookmark_artwork_with_artist_map(
            bookmark_artwork=bookmark_artwork,
            artist_map=artist_map,
        )

    def match_all(self) -> dict:
        bookmark_artworks = self.bookmark_artwork_repo.get_all()
        artist_map = self.artist_repo.get_pixiv_id_map()

        matched_count = 0
        unmatched_count = 0

        for bookmark_artwork in bookmark_artworks:
            matched_artwork = self._match_bookmark_artwork_with_artist_map(
                bookmark_artwork=bookmark_artwork,
                artist_map=artist_map,
            )

            local_artist_id = matched_artwork.get("local_artist_id")
            is_matched = local_artist_id is not None

            self.bookmark_artwork_repo.update_local_match(
                bookmark_artwork_id=bookmark_artwork["id"],
                local_artist_id=local_artist_id,
            )

            if is_matched:
                matched_count += 1
            else:
                unmatched_count += 1

        return {
            "total_count": len(bookmark_artworks),
            "matched_count": matched_count,
            "unmatched_count": unmatched_count,
        }

    def _match_bookmark_artwork_with_artist_map(
        self,
        bookmark_artwork: dict,
        artist_map: dict[str, dict],
    ) -> dict:
        artist_id = str(
            bookmark_artwork.get("artist_id", "") or ""
        ).strip()

        if not artist_id:
            return self._build_unmatched_result(bookmark_artwork)

        artist = artist_map.get(artist_id)

        if artist is None:
            return self._build_unmatched_result(bookmark_artwork)

        matched_artwork = dict(bookmark_artwork)
        matched_artwork["local_artist_id"] = artist["id"]
        matched_artwork["is_local_artist"] = 1

        return matched_artwork

    def _build_unmatched_result(
        self,
        bookmark_artwork: dict,
    ) -> dict:
        unmatched_artwork = dict(bookmark_artwork)
        unmatched_artwork["local_artist_id"] = None
        unmatched_artwork["is_local_artist"] = 0

        return unmatched_artwork
