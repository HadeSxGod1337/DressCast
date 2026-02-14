"""Cities use cases: ListCities, AddCity, GetCity, ListAllCoordinates."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from users.domain.entities import City
from users.domain.exceptions import CityNotFoundError
from users.infrastructure.db.repositories.city_repository import CityRepositoryImpl
from users.infrastructure.db.session import get_session


class ListCitiesUseCase:
    def __init__(
        self,
        city_repository: CityRepositoryImpl,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._city_repo = city_repository
        self._session_factory = session_factory

    async def run(self, user_id: int) -> list[City]:
        async with get_session(self._session_factory) as session:
            return await self._city_repo.list_by_user_id(session, user_id)


class AddCityUseCase:
    def __init__(
        self,
        city_repository: CityRepositoryImpl,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._city_repo = city_repository
        self._session_factory = session_factory

    async def run(self, user_id: int, name: str, lat: float, lon: float) -> City:
        async with get_session(self._session_factory) as session:
            return await self._city_repo.add(session, user_id, name, lat, lon)


class GetCityUseCase:
    def __init__(
        self,
        city_repository: CityRepositoryImpl,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._city_repo = city_repository
        self._session_factory = session_factory

    async def run(self, user_id: int, city_name: str) -> City:
        async with get_session(self._session_factory) as session:
            city = await self._city_repo.get_by_user_and_name(session, user_id, city_name)
            if city is None:
                raise CityNotFoundError(f"City {city_name} not found")
            return city


class ListAllCoordinatesUseCase:
    def __init__(
        self,
        city_repository: CityRepositoryImpl,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._city_repo = city_repository
        self._session_factory = session_factory

    async def run(self) -> list[tuple[int, float, float]]:
        async with get_session(self._session_factory) as session:
            return await self._city_repo.list_all_coordinates(session)
