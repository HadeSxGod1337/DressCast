"""Gateway client for Telegram bot (gRPC stub wrapper)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import gateway_pb2
import gateway_pb2_grpc
from grpc import aio


class GatewayClient:
    def __init__(self, gateway_addr: str):
        self._addr = gateway_addr
        self._channel: aio.Channel | None = None
        self._stub = None

    async def get_stub(self):
        if self._stub is None:
            self._channel = aio.insecure_channel(self._addr)
            self._stub = gateway_pb2_grpc.GatewayServiceStub(self._channel)
        return self._stub

    async def get_or_create_user_by_telegram(
        self, telegram_id: str, username: str = "", locale: str = "en"
    ):
        s = await self.get_stub()
        return await s.GetOrCreateUserByTelegramId(
            gateway_pb2.GetOrCreateUserByTelegramIdGatewayRequest(
                telegram_id=telegram_id, username=username, locale=locale
            )
        )

    async def list_cities(self, user_id: int):
        s = await self.get_stub()
        return await s.ListUserCities(gateway_pb2.ListUserCitiesRequest(user_id=user_id))

    async def add_city(self, user_id: int, name: str, lat: float, lon: float):
        s = await self.get_stub()
        return await s.AddCity(
            gateway_pb2.AddCityGatewayRequest(user_id=user_id, name=name, lat=lat, lon=lon)
        )

    async def get_forecast(self, user_id: int, city_name: str, date: str = "", time: str = ""):
        s = await self.get_stub()
        return await s.GetForecast(
            gateway_pb2.GatewayForecastRequest(
                user_id=user_id, city_name=city_name, date=date, time=time
            )
        )

    async def get_dress_advice(self, user_id: int, city_name: str, locale: str = "en"):
        s = await self.get_stub()
        return await s.GetDressAdvice(
            gateway_pb2.GetDressAdviceRequest(user_id=user_id, city_name=city_name, locale=locale)
        )
