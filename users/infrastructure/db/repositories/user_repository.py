"""User repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from users.domain.entities import User
from users.domain.exceptions import UserAlreadyExistsError
from users.infrastructure.db.models import UserModel


class UserRepositoryImpl:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create(
        self,
        session: AsyncSession,
        username: str,
        password_hash: str,
        telegram_id: str | None = None,
        is_admin: bool = False,
        locale: str = "en",
    ) -> User:
        result = await session.execute(select(UserModel).where(UserModel.username == username))
        if result.scalar_one_or_none():
            raise UserAlreadyExistsError(f"Username {username} already exists")
        model = UserModel(
            username=username,
            password_hash=password_hash,
            telegram_id=telegram_id,
            is_admin=is_admin,
            locale=locale,
        )
        session.add(model)
        await session.flush()
        await session.refresh(model)
        return User(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            telegram_id=model.telegram_id,
            is_admin=model.is_admin,
            locale=model.locale,
        )

    async def get_by_username(self, session: AsyncSession, username: str) -> User | None:
        result = await session.execute(select(UserModel).where(UserModel.username == username))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return User(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            telegram_id=model.telegram_id,
            is_admin=model.is_admin,
            locale=model.locale,
        )

    async def get_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        result = await session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return User(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            telegram_id=model.telegram_id,
            is_admin=model.is_admin,
            locale=model.locale,
        )

    async def get_by_telegram_id(self, session: AsyncSession, telegram_id: str) -> User | None:
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return User(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            telegram_id=model.telegram_id,
            is_admin=model.is_admin,
            locale=model.locale,
        )
