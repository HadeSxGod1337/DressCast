"""Gateway entry point (composition root): FastAPI + gRPC."""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from grpc import aio

from gateway.config.settings import Settings

_settings = Settings()
logging.basicConfig(
    level=getattr(logging, _settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

import gateway_pb2_grpc

from gateway.api.grpc.servicer import GatewayServicer
from gateway.api.v1.auth import router as auth_router
from gateway.api.v1.routes import router as api_router
from gateway.api.v2.routes import router as api_v2_router
from gateway.application.use_cases.cities import AddCityUseCase, ListUserCitiesUseCase
from gateway.application.use_cases.dress_advice import GetDressAdviceForUserCityUseCase
from gateway.application.use_cases.forecast import GetForecastForUserCityUseCase
from gateway.application.use_cases.users import GetOrCreateUserByTelegramIdUseCase

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = _settings
    get_forecast_uc = GetForecastForUserCityUseCase(
        settings.users_grpc_addr, settings.weather_grpc_addr
    )
    get_dress_advice_uc = GetDressAdviceForUserCityUseCase(
        settings.users_grpc_addr,
        settings.weather_grpc_addr,
        settings.dress_advice_grpc_addr,
    )
    list_cities_uc = ListUserCitiesUseCase(settings.users_grpc_addr)
    add_city_uc = AddCityUseCase(settings.users_grpc_addr)
    get_or_create_telegram_uc = GetOrCreateUserByTelegramIdUseCase(settings.users_grpc_addr)
    servicer = GatewayServicer(
        get_forecast_uc=get_forecast_uc,
        get_dress_advice_uc=get_dress_advice_uc,
        list_cities_uc=list_cities_uc,
        add_city_uc=add_city_uc,
        get_or_create_telegram_uc=get_or_create_telegram_uc,
    )
    server = aio.server()
    gateway_pb2_grpc.add_GatewayServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"{settings.grpc_host}:{settings.grpc_port}")
    await server.start()
    app.state.grpc_server = server
    logger.info("Gateway gRPC listening on %s:%s", settings.grpc_host, settings.grpc_port)
    yield
    await server.stop(grace=2)


app = FastAPI(title="DressCast Gateway", version="0.1.0", lifespan=lifespan)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(api_router)
app.include_router(api_v2_router)


@app.get("/health")
def health():
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    settings = _settings
    uvicorn.run(
        "gateway.main:app",
        host=settings.http_host,
        port=settings.http_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
