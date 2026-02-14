"""Weather service entry point (composition root)."""

import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import weather_pb2_grpc
from grpc import aio

from weather.api.servicer import WeatherServicer
from weather.application.use_cases.get_forecast import (
    GetCurrentWeatherUseCase,
    GetForecastUseCase,
    RefreshForecastsUseCase,
)
from weather.config.settings import Settings
from weather.infrastructure.cache.redis_cache import RedisForecastCache
from weather.infrastructure.external.open_meteo import OpenMeteoProvider

logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    provider = OpenMeteoProvider()
    try:
        cache = RedisForecastCache(settings.redis_url)
    except Exception:
        cache = None
        logger.warning("Redis unavailable, running without cache")
    get_current_uc = GetCurrentWeatherUseCase(provider, cache)
    get_forecast_uc = GetForecastUseCase(provider, cache)
    refresh_uc = RefreshForecastsUseCase(provider)
    servicer = WeatherServicer(get_current_uc, get_forecast_uc, refresh_uc)

    async def serve() -> None:
        server = aio.server()
        weather_pb2_grpc.add_WeatherServiceServicer_to_server(servicer, server)
        server.add_insecure_port(f"{settings.grpc_host}:{settings.grpc_port}")
        await server.start()
        logger.info(
            "Weather gRPC server listening on %s:%s", settings.grpc_host, settings.grpc_port
        )
        await server.wait_for_termination()

    asyncio.run(serve())


if __name__ == "__main__":
    main()
