"""GetOrCreateUserByTelegramId use case."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from users.domain.entities import User
from users.infrastructure.db.repositories.user_repository import UserRepositoryImpl
from users.infrastructure.db.session import get_session


class GetOrCreateUserByTelegramIdUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryImpl,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._user_repo = user_repository
        self._session_factory = session_factory

    async def run(self, telegram_id: str, username: str | None = None, locale: str = "en") -> User:
        async with get_session(self._session_factory) as session:
            user = await self._user_repo.get_by_telegram_id(session, telegram_id)
            if user is not None:
                return user
            name = username or f"tg_{telegram_id}"
            return await self._user_repo.create(
                session,
                username=name,
                password_hash="",
                telegram_id=telegram_id,
                locale=locale,  # nosec B106 - Telegram users have no password
            )
