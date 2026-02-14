"""gRPC servicer: delegates to use cases and maps exceptions."""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import common_pb2
import grpc
import users_pb2
import users_pb2_grpc

from users.api.errors import domain_error_to_grpc
from users.domain.exceptions import DomainError

logger = logging.getLogger(__name__)


class UsersServicer(users_pb2_grpc.UsersServiceServicer):
    def __init__(
        self,
        create_user,
        get_user_by_username,
        get_user_by_id,
        add_city,
        list_cities,
        get_city,
        get_or_create_user_by_telegram_id,
        list_all_coordinates,
    ):
        self._create_user = create_user
        self._get_user_by_username = get_user_by_username
        self._get_user_by_id = get_user_by_id
        self._add_city = add_city
        self._list_cities = list_cities
        self._get_city = get_city
        self._get_or_create_user_by_telegram_id = get_or_create_user_by_telegram_id
        self._list_all_coordinates = list_all_coordinates

    @staticmethod
    def _user_to_proto(user):
        return common_pb2.User(
            id=user.id,
            username=user.username,
            telegram_id=user.telegram_id or "",
            is_admin=user.is_admin,
            locale=user.locale,
        )

    @staticmethod
    def _city_to_proto(city):
        return common_pb2.City(
            id=city.id,
            user_id=city.user_id,
            name=city.name,
            lat=city.lat,
            lon=city.lon,
        )

    async def CreateUser(self, request, context):
        logger.info("CreateUser username=%s", request.username)
        try:
            user = await self._create_user.run(
                username=request.username,
                password_hash=request.password_hash,
            )
            return users_pb2.CreateUserResponse(user=self._user_to_proto(user))
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "CreateUser DomainError username=%s code=%s",
                request.username,
                getattr(e, "code", e),
            )
            context.set_code(code)
            context.set_details(msg)
            return users_pb2.CreateUserResponse()
        except Exception as e:
            logger.exception("CreateUser failed username=%s: %s", request.username, e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return users_pb2.CreateUserResponse()

    async def GetUserByUsername(self, request, context):
        logger.info("GetUserByUsername username=%s", request.username)
        try:
            user = await self._get_user_by_username.run(username=request.username)
            return self._user_to_proto(user)
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "GetUserByUsername DomainError username=%s code=%s",
                request.username,
                getattr(e, "code", e),
            )
            context.set_code(code)
            context.set_details(msg)
            return common_pb2.User()
        except Exception as e:
            logger.exception("GetUserByUsername failed username=%s: %s", request.username, e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return common_pb2.User()

    async def GetUserById(self, request, context):
        logger.info("GetUserById user_id=%s", request.user_id)
        try:
            user = await self._get_user_by_id.run(user_id=request.user_id)
            return self._user_to_proto(user)
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "GetUserById DomainError user_id=%s code=%s", request.user_id, getattr(e, "code", e)
            )
            context.set_code(code)
            context.set_details(msg)
            return common_pb2.User()
        except Exception as e:
            logger.exception("GetUserById failed user_id=%s: %s", request.user_id, e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return common_pb2.User()

    async def AddCity(self, request, context):
        logger.info(
            "AddCity user_id=%s name=%s lat=%s lon=%s",
            request.user_id,
            request.name,
            request.lat,
            request.lon,
        )
        try:
            city = await self._add_city.run(
                user_id=request.user_id,
                name=request.name,
                lat=request.lat,
                lon=request.lon,
            )
            return self._city_to_proto(city)
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "AddCity DomainError user_id=%s name=%s code=%s",
                request.user_id,
                request.name,
                getattr(e, "code", e),
            )
            context.set_code(code)
            context.set_details(msg)
            return common_pb2.City()
        except Exception as e:
            logger.exception(
                "AddCity failed user_id=%s name=%s: %s", request.user_id, request.name, e
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return common_pb2.City()

    async def ListCities(self, request, context):
        logger.info("ListCities user_id=%s", request.user_id)
        try:
            cities = await self._list_cities.run(user_id=request.user_id)
            return users_pb2.ListCitiesResponse(cities=[self._city_to_proto(c) for c in cities])
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "ListCities DomainError user_id=%s code=%s", request.user_id, getattr(e, "code", e)
            )
            context.set_code(code)
            context.set_details(msg)
            return users_pb2.ListCitiesResponse()
        except Exception as e:
            logger.exception("ListCities failed user_id=%s: %s", request.user_id, e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return users_pb2.ListCitiesResponse()

    async def GetCity(self, request, context):
        logger.info("GetCity user_id=%s city_name=%s", request.user_id, request.city_name)
        try:
            city = await self._get_city.run(user_id=request.user_id, city_name=request.city_name)
            return self._city_to_proto(city)
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "GetCity DomainError user_id=%s city_name=%s code=%s",
                request.user_id,
                request.city_name,
                getattr(e, "code", e),
            )
            context.set_code(code)
            context.set_details(msg)
            return common_pb2.City()
        except Exception as e:
            logger.exception(
                "GetCity failed user_id=%s city_name=%s: %s", request.user_id, request.city_name, e
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return common_pb2.City()

    async def GetOrCreateUserByTelegramId(self, request, context):
        logger.info(
            "GetOrCreateUserByTelegramId telegram_id=%s locale=%s",
            request.telegram_id,
            request.locale or "en",
        )
        try:
            user = await self._get_or_create_user_by_telegram_id.run(
                telegram_id=request.telegram_id,
                username=request.username or None,
                locale=request.locale or "en",
            )
            return self._user_to_proto(user)
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "GetOrCreateUserByTelegramId DomainError telegram_id=%s code=%s",
                request.telegram_id,
                getattr(e, "code", e),
            )
            context.set_code(code)
            context.set_details(msg)
            return common_pb2.User()
        except Exception as e:
            logger.exception(
                "GetOrCreateUserByTelegramId failed telegram_id=%s: %s", request.telegram_id, e
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return common_pb2.User()

    async def ListAllCoordinates(self, _request, context):
        logger.info("ListAllCoordinates")
        try:
            coords = await self._list_all_coordinates.run()
            return users_pb2.ListAllCoordinatesResponse(
                coords=[
                    users_pb2.CoordWithUserId(user_id=uid, lat=lat, lon=lon)
                    for uid, lat, lon in coords
                ]
            )
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning("ListAllCoordinates DomainError code=%s", getattr(e, "code", e))
            context.set_code(code)
            context.set_details(msg)
            return users_pb2.ListAllCoordinatesResponse()
        except Exception as e:
            logger.exception("ListAllCoordinates failed: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return users_pb2.ListAllCoordinatesResponse()
