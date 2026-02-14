"""Gateway gRPC servicer: delegates to use cases, maps exceptions."""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import common_pb2
import gateway_pb2
import gateway_pb2_grpc
import grpc

from gateway.api.v1.errors import message_for_code

logger = logging.getLogger(__name__)


class GatewayServicer(gateway_pb2_grpc.GatewayServiceServicer):
    def __init__(
        self,
        get_forecast_uc,
        get_dress_advice_uc,
        list_cities_uc,
        add_city_uc,
        get_or_create_telegram_uc,
    ):
        self._get_forecast = get_forecast_uc
        self._get_dress_advice = get_dress_advice_uc
        self._list_cities = list_cities_uc
        self._add_city = add_city_uc
        self._get_or_create_telegram = get_or_create_telegram_uc

    def _set_error(self, context, code: str, grpc_code: grpc.StatusCode, locale: str = "en"):
        context.set_code(grpc_code)
        context.set_details(message_for_code(code, locale))

    async def GetForecast(self, request, context):
        logger.info(
            "GetForecast user_id=%s city_name=%s date=%s time=%s",
            request.user_id,
            request.city_name,
            request.date or "",
            request.time or "",
        )
        try:
            result = await self._get_forecast.run(
                request.user_id,
                request.city_name,
                request.date or "",
                request.time or "",
            )
            return gateway_pb2.GatewayForecastResponse(weather_data=result.data)
        except ValueError as e:
            if "CITY_NOT_FOUND" in str(e):
                logger.warning(
                    "GetForecast CITY_NOT_FOUND user_id=%s city_name=%s",
                    request.user_id,
                    request.city_name,
                )
                self._set_error(context, "CITY_NOT_FOUND", grpc.StatusCode.NOT_FOUND)
            else:
                logger.warning("GetForecast ValueError user_id=%s: %s", request.user_id, e)
                context.set_code(grpc.StatusCode.UNKNOWN)
                context.set_details(str(e))
            return gateway_pb2.GatewayForecastResponse()
        except Exception as e:
            logger.exception(
                "GetForecast failed user_id=%s city_name=%s: %s",
                request.user_id,
                request.city_name,
                e,
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return gateway_pb2.GatewayForecastResponse()

    async def GetDressAdvice(self, request, context):
        logger.info(
            "GetDressAdvice user_id=%s city_name=%s locale=%s",
            request.user_id,
            request.city_name,
            request.locale or "en",
        )
        try:
            result = await self._get_dress_advice.run(
                request.user_id,
                request.city_name,
                request.date or "",
                request.time or "",
                request.locale or "en",
            )
            return gateway_pb2.GetDressAdviceResponse(advice_text=result.advice_text)
        except ValueError as e:
            if "CITY_NOT_FOUND" in str(e):
                logger.warning(
                    "GetDressAdvice CITY_NOT_FOUND user_id=%s city_name=%s",
                    request.user_id,
                    request.city_name,
                )
                self._set_error(context, "CITY_NOT_FOUND", grpc.StatusCode.NOT_FOUND)
            else:
                logger.warning("GetDressAdvice ValueError user_id=%s: %s", request.user_id, e)
                context.set_code(grpc.StatusCode.UNKNOWN)
                context.set_details(str(e))
            return gateway_pb2.GetDressAdviceResponse(advice_text="")
        except Exception as e:
            logger.exception(
                "GetDressAdvice failed user_id=%s city_name=%s: %s",
                request.user_id,
                request.city_name,
                e,
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return gateway_pb2.GetDressAdviceResponse(advice_text="")

    async def ListUserCities(self, request, context):
        logger.info("ListUserCities user_id=%s", request.user_id)
        try:
            result = await self._list_cities.run(request.user_id)
            return gateway_pb2.ListUserCitiesResponse(cities=result.cities)
        except Exception as e:
            logger.exception("ListUserCities failed user_id=%s: %s", request.user_id, e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return gateway_pb2.ListUserCitiesResponse()

    async def AddCity(self, request, context):
        logger.info(
            "AddCity user_id=%s name=%s lat=%s lon=%s",
            request.user_id,
            request.name,
            request.lat,
            request.lon,
        )
        try:
            result = await self._add_city.run(
                request.user_id,
                request.name,
                request.lat,
                request.lon,
            )
            return result
        except Exception as e:
            logger.exception(
                "AddCity failed user_id=%s name=%s: %s", request.user_id, request.name, e
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
            result = await self._get_or_create_telegram.run(
                request.telegram_id,
                request.username or "",
                request.locale or "en",
            )
            return result
        except Exception as e:
            logger.exception(
                "GetOrCreateUserByTelegramId failed telegram_id=%s: %s", request.telegram_id, e
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return common_pb2.User()
