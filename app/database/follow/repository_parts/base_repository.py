from app.database.follow.update_repository import FollowUserUpdateRepository

from .mutation_repository import FollowUserMutationRepository
from .query_repository import FollowUserQueryRepository


class FollowUserRepository(
    FollowUserMutationRepository,
    FollowUserQueryRepository,
    FollowUserUpdateRepository,
):
    pass
