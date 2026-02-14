"""Users service entry point (composition root)."""

import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import bcrypt
import users_pb2_grpc
from grpc import aio

from users.api.servicer import UsersServicer
from users.application.use_cases.cities import (
    AddCityUseCase,
    GetCityUseCase,
    ListAllCoordinatesUseCase,
    ListCitiesUseCase,
)
from users.application.use_cases.create_user import CreateUserUseCase
from users.application.use_cases.get_user_by_id import GetUserByIdUseCase
from users.application.use_cases.get_user_by_username import GetUserByUsernameUseCase
from users.application.use_cases.telegram import GetOrCreateUserByTelegramIdUseCase
from users.config.settings import Settings
from users.infrastructure.db.repositories.city_repository import CityRepositoryImpl
from users.infrastructure.db.repositories.user_repository import UserRepositoryImpl
from users.infrastructure.db.session import get_session_factory, init_db

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    raw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


async def _create_admin_if_configured(settings: Settings, create_user: CreateUserUseCase) -> None:
    if not settings.create_admin_username:
        return
    try:
        await create_user.run(
            username=settings.create_admin_username,
            password_hash=_hash_password("admin"),
            is_admin=True,
        )
        logger.info("Admin user '%s' created.", settings.create_admin_username)
    except Exception as e:
        if "already exists" in str(e).lower() or "unique" in str(e).lower():
            logger.debug("Admin user already exists, skipping")
        else:
            raise


def main() -> None:
    settings = Settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    session_factory = get_session_factory(settings)

    user_repo = UserRepositoryImpl(session_factory)
    city_repo = CityRepositoryImpl(session_factory)

    create_user_uc = CreateUserUseCase(user_repo, session_factory)
    get_user_by_username_uc = GetUserByUsernameUseCase(user_repo, session_factory)
    get_user_by_id_uc = GetUserByIdUseCase(user_repo, session_factory)
    list_cities_uc = ListCitiesUseCase(city_repo, session_factory)
    add_city_uc = AddCityUseCase(city_repo, session_factory)
    get_city_uc = GetCityUseCase(city_repo, session_factory)
    get_or_create_telegram_uc = GetOrCreateUserByTelegramIdUseCase(user_repo, session_factory)
    list_all_coords_uc = ListAllCoordinatesUseCase(city_repo, session_factory)

    servicer = UsersServicer(
        create_user=create_user_uc,
        get_user_by_username=get_user_by_username_uc,
        get_user_by_id=get_user_by_id_uc,
        add_city=add_city_uc,
        list_cities=list_cities_uc,
        get_city=get_city_uc,
        get_or_create_user_by_telegram_id=get_or_create_telegram_uc,
        list_all_coordinates=list_all_coords_uc,
    )

    async def serve() -> None:
        await init_db(settings)
        await _create_admin_if_configured(settings, create_user_uc)
        server = aio.server()
        users_pb2_grpc.add_UsersServiceServicer_to_server(servicer, server)
        server.add_insecure_port(f"{settings.grpc_host}:{settings.grpc_port}")
        await server.start()
        logger.info("Users gRPC server listening on %s:%s", settings.grpc_host, settings.grpc_port)
        await server.wait_for_termination()

    asyncio.run(serve())


if __name__ == "__main__":
    main()
