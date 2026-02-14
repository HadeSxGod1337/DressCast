"""CreateUser use case."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from users.domain.entities import User
from users.infrastructure.db.repositories.user_repository import UserRepositoryImpl
from users.infrastructure.db.session import get_session


class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryImpl,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._user_repo = user_repository
        self._session_factory = session_factory

    async def run(
        self,
        username: str,
        password_hash: str,
        telegram_id: str | None = None,
        is_admin: bool = False,
        locale: str = "en",
    ) -> User:
        async with get_session(self._session_factory) as session:
            return await self._user_repo.create(
                session, username, password_hash, telegram_id, is_admin, locale
            )
