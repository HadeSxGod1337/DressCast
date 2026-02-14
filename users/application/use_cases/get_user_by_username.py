"""GetUserByUsername use case."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from users.domain.entities import User
from users.domain.exceptions import UserNotFoundError
from users.infrastructure.db.repositories.user_repository import UserRepositoryImpl
from users.infrastructure.db.session import get_session


class GetUserByUsernameUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryImpl,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._user_repo = user_repository
        self._session_factory = session_factory

    async def run(self, username: str) -> User:
        async with get_session(self._session_factory) as session:
            user = await self._user_repo.get_by_username(session, username)
            if user is None:
                raise UserNotFoundError(f"User {username} not found")
            return user
