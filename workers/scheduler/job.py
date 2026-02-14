"""RefreshForecastsJob: ListAllCoordinates -> RefreshForecasts."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import common_pb2
import users_pb2
import weather_pb2

from workers.scheduler.clients import RefreshClients


class RefreshForecastsJob:
    def __init__(self, clients: RefreshClients):
        self._clients = clients

    async def run(self) -> None:
        users = await self._clients.get_users_stub()
        weather = await self._clients.get_weather_stub()
        resp = await users.ListAllCoordinates(users_pb2.ListAllCoordinatesRequest())
        if not resp.coords:
            return
        coords = [common_pb2.Coordinate(lat=c.lat, lon=c.lon) for c in resp.coords]
        await weather.RefreshForecasts(weather_pb2.RefreshForecastsRequest(coords=coords))
