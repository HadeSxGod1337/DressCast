"""ListUserCities, AddCity, GetCity via Users stub."""

import users_pb2

from gateway.infrastructure.grpc_clients.clients import users_stub


class ListUserCitiesUseCase:
    def __init__(self, users_address: str):
        self._users_addr = users_address

    async def run(self, user_id: int):
        u = await users_stub(self._users_addr)
        return await u.ListCities(users_pb2.ListCitiesRequest(user_id=user_id))


class AddCityUseCase:
    def __init__(self, users_address: str):
        self._users_addr = users_address

    async def run(self, user_id: int, name: str, lat: float, lon: float):
        u = await users_stub(self._users_addr)
        return await u.AddCity(
            users_pb2.AddCityRequest(user_id=user_id, name=name, lat=lat, lon=lon)
        )


class GetCityUseCase:
    def __init__(self, users_address: str):
        self._users_addr = users_address

    async def run(self, user_id: int, city_name: str):
        u = await users_stub(self._users_addr)
        return await u.GetCity(users_pb2.GetCityRequest(user_id=user_id, city_name=city_name))
