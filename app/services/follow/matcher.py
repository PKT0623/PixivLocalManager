from app.database import ArtistRepository, FollowUserRepository


class FollowUserMatcher:
    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.follow_user_repo = FollowUserRepository()

    def get_artist_map(self) -> dict[str, dict]:
        return self.artist_repo.get_pixiv_id_map()

    def match_follow_user(
        self,
        follow_user: dict,
        artist_map: dict[str, dict] | None = None,
    ) -> dict:
        if artist_map is None:
            artist_map = self.get_artist_map()

        return self._match_follow_user_with_artist_map(
            follow_user=follow_user,
            artist_map=artist_map,
        )

    def match_follow_users(
        self,
        follow_users: list[dict],
        artist_map: dict[str, dict] | None = None,
    ) -> list[dict]:
        if artist_map is None:
            artist_map = self.get_artist_map()

        return [
            self._match_follow_user_with_artist_map(
                follow_user=follow_user,
                artist_map=artist_map,
            )
            for follow_user in follow_users
        ]

    def match_all(self) -> dict:
        follow_users = self.follow_user_repo.get_all()
        artist_map = self.get_artist_map()

        matched_count = 0
        unmatched_count = 0

        for follow_user in follow_users:
            matched_user = self._match_follow_user_with_artist_map(
                follow_user=follow_user,
                artist_map=artist_map,
            )

            local_artist_id = matched_user.get("local_artist_id")
            is_matched = local_artist_id is not None

            self.follow_user_repo.update_local_match(
                follow_user_id=follow_user["id"],
                local_artist_id=local_artist_id,
            )

            if is_matched:
                matched_count += 1
            else:
                unmatched_count += 1

        return {
            "total_count": len(follow_users),
            "matched_count": matched_count,
            "unmatched_count": unmatched_count,
        }

    def _match_follow_user_with_artist_map(
        self,
        follow_user: dict,
        artist_map: dict[str, dict],
    ) -> dict:
        pixiv_user_id = str(
            follow_user.get("pixiv_user_id", "") or ""
        ).strip()

        if not pixiv_user_id:
            return self._build_unmatched_result(follow_user)

        artist = artist_map.get(pixiv_user_id)

        if artist is None:
            return self._build_unmatched_result(follow_user)

        matched_user = dict(follow_user)
        matched_user["local_artist_id"] = artist["id"]
        matched_user["is_local_artist"] = 1
        matched_user["file_count"] = int(
            artist.get("folder_file_count", 0) or 0
        )

        return matched_user

    def _build_unmatched_result(
        self,
        follow_user: dict,
    ) -> dict:
        unmatched_user = dict(follow_user)
        unmatched_user["local_artist_id"] = None
        unmatched_user["is_local_artist"] = 0

        return unmatched_user
