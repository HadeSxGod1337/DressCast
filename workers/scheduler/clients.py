"""RefreshClients: gRPC stubs for Users and Weather."""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import users_pb2_grpc
import weather_pb2_grpc
from grpc import aio

logger = logging.getLogger(__name__)


class RefreshClients:
    def __init__(self, users_addr: str, weather_addr: str):
        self._users_addr = users_addr
        self._weather_addr = weather_addr
        self._users_channel: aio.Channel | None = None
        self._weather_channel: aio.Channel | None = None

    async def get_users_stub(self) -> users_pb2_grpc.UsersServiceStub:
        if self._users_channel is None:
            logger.debug("Scheduler Users channel created addr=%s", self._users_addr)
            self._users_channel = aio.insecure_channel(self._users_addr)
        return users_pb2_grpc.UsersServiceStub(self._users_channel)

    async def get_weather_stub(self) -> weather_pb2_grpc.WeatherServiceStub:
        if self._weather_channel is None:
            logger.debug("Scheduler Weather channel created addr=%s", self._weather_addr)
            self._weather_channel = aio.insecure_channel(self._weather_addr)
        return weather_pb2_grpc.WeatherServiceStub(self._weather_channel)
