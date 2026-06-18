from app.database import ArtistRepository, FollowUserRepository


class FollowUserMatcher:
    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.follow_user_repo = FollowUserRepository()

    def match_follow_user(
        self,
        follow_user: dict,
    ) -> dict:
        pixiv_user_id = str(
            follow_user.get("pixiv_user_id", "") or ""
        ).strip()

        if not pixiv_user_id:
            return self._build_unmatched_result(follow_user)

        artist = self.artist_repo.get_by_pixiv_id(pixiv_user_id)

        if artist is None:
            return self._build_unmatched_result(follow_user)

        matched_user = dict(follow_user)
        matched_user["local_artist_id"] = artist["id"]
        matched_user["is_local_artist"] = 1
        matched_user["file_count"] = int(
            artist.get("folder_file_count", 0) or 0
        )

        return matched_user

    def match_all(self) -> dict:
        follow_users = self.follow_user_repo.get_all()

        matched_count = 0
        unmatched_count = 0

        for follow_user in follow_users:
            matched_user = self.match_follow_user(follow_user)

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

    def _build_unmatched_result(
        self,
        follow_user: dict,
    ) -> dict:
        unmatched_user = dict(follow_user)
        unmatched_user["local_artist_id"] = None
        unmatched_user["is_local_artist"] = 0

        return unmatched_user
