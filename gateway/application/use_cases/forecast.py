"""GetForecastForUserCity: get city coords from Users, then forecast from Weather."""

import users_pb2
import weather_pb2

from gateway.infrastructure.grpc_clients.clients import users_stub, weather_stub


class GetForecastForUserCityUseCase:
    def __init__(self, users_address: str, weather_address: str):
        self._users_addr = users_address
        self._weather_addr = weather_address

    async def run(self, user_id: int, city_name: str, date: str = "", time: str = ""):
        u = await users_stub(self._users_addr)
        city = await u.GetCity(users_pb2.GetCityRequest(user_id=user_id, city_name=city_name))
        if not city.name:
            raise ValueError("CITY_NOT_FOUND")
        w = await weather_stub(self._weather_addr)
        return await w.GetForecast(
            weather_pb2.GetForecastRequest(lat=city.lat, lon=city.lon, date=date, time=time)
        )
