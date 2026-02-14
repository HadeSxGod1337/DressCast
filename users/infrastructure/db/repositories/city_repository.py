"""City repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from users.domain.entities import City
from users.domain.exceptions import CityAlreadyExistsError
from users.infrastructure.db.models import CityModel


class CityRepositoryImpl:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def add(
        self, session: AsyncSession, user_id: int, name: str, lat: float, lon: float
    ) -> City:
        result = await session.execute(
            select(CityModel).where(CityModel.user_id == user_id, CityModel.name == name)
        )
        if result.scalar_one_or_none():
            raise CityAlreadyExistsError(f"City {name} already exists for user")
        model = CityModel(user_id=user_id, name=name, lat=lat, lon=lon)
        session.add(model)
        await session.flush()
        await session.refresh(model)
        return City(
            id=model.id, user_id=model.user_id, name=model.name, lat=model.lat, lon=model.lon
        )

    async def list_by_user_id(self, session: AsyncSession, user_id: int) -> list[City]:
        result = await session.execute(select(CityModel).where(CityModel.user_id == user_id))
        return [
            City(id=m.id, user_id=m.user_id, name=m.name, lat=m.lat, lon=m.lon)
            for m in result.scalars().all()
        ]

    async def get_by_user_and_name(
        self, session: AsyncSession, user_id: int, city_name: str
    ) -> City | None:
        result = await session.execute(
            select(CityModel).where(CityModel.user_id == user_id, CityModel.name == city_name)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return City(
            id=model.id, user_id=model.user_id, name=model.name, lat=model.lat, lon=model.lon
        )

    async def list_all_coordinates(self, session: AsyncSession) -> list[tuple[int, float, float]]:
        result = await session.execute(select(CityModel.user_id, CityModel.lat, CityModel.lon))
        return list(result.all())
