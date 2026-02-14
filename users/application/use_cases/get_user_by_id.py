"""GetUserById use case."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from users.domain.entities import User
from users.domain.exceptions import UserNotFoundError
from users.infrastructure.db.repositories.user_repository import UserRepositoryImpl
from users.infrastructure.db.session import get_session


class GetUserByIdUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryImpl,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._user_repo = user_repository
        self._session_factory = session_factory

    async def run(self, user_id: int) -> User:
        async with get_session(self._session_factory) as session:
            user = await self._user_repo.get_by_id(session, user_id)
            if user is None:
                raise UserNotFoundError(f"User id {user_id} not found")
            return user
