"""gRPC servicer: delegates to use cases, maps exceptions."""

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
import weather_pb2
import weather_pb2_grpc

from weather.api.errors import domain_error_to_grpc
from weather.domain.exceptions import DomainError

logger = logging.getLogger(__name__)


def _weather_data_to_proto(data) -> common_pb2.WeatherData:
    return common_pb2.WeatherData(
        temperature=data.temperature,
        humidity=data.humidity,
        wind_speed=data.wind_speed,
        precipitation=data.precipitation,
        time=data.time,
    )


class WeatherServicer(weather_pb2_grpc.WeatherServiceServicer):
    def __init__(self, get_current_weather_uc, get_forecast_uc, refresh_forecasts_uc):
        self._get_current = get_current_weather_uc
        self._get_forecast = get_forecast_uc
        self._refresh = refresh_forecasts_uc

    async def GetCurrentWeather(self, request, context):
        logger.info("GetCurrentWeather lat=%s lon=%s", request.lat, request.lon)
        try:
            data = await self._get_current.run(lat=request.lat, lon=request.lon)
            return _weather_data_to_proto(data)
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "GetCurrentWeather DomainError lat=%s lon=%s code=%s",
                request.lat,
                request.lon,
                getattr(e, "code", e),
            )
            context.set_code(code)
            context.set_details(msg)
            return common_pb2.WeatherData()
        except Exception as e:
            logger.exception(
                "GetCurrentWeather failed lat=%s lon=%s: %s", request.lat, request.lon, e
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return common_pb2.WeatherData()

    async def GetForecast(self, request, context):
        logger.info(
            "GetForecast lat=%s lon=%s date=%s time=%s",
            request.lat,
            request.lon,
            request.date or "",
            request.time or "",
        )
        try:
            data = await self._get_forecast.run(
                lat=request.lat,
                lon=request.lon,
                date=request.date or "",
                time=request.time or "",
            )
            return weather_pb2.GetForecastResponse(data=_weather_data_to_proto(data))
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning(
                "GetForecast DomainError lat=%s lon=%s code=%s",
                request.lat,
                request.lon,
                getattr(e, "code", e),
            )
            context.set_code(code)
            context.set_details(msg)
            return weather_pb2.GetForecastResponse()
        except Exception as e:
            logger.exception("GetForecast failed lat=%s lon=%s: %s", request.lat, request.lon, e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return weather_pb2.GetForecastResponse()

    async def RefreshForecasts(self, request, context):
        coords = [(c.lat, c.lon) for c in request.coords]
        logger.info("RefreshForecasts coords_count=%s", len(coords))
        try:
            count = await self._refresh.run(coords)
            return weather_pb2.RefreshForecastsResponse(refreshed_count=count)
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning("RefreshForecasts DomainError code=%s", getattr(e, "code", e))
            context.set_code(code)
            context.set_details(msg)
            return weather_pb2.RefreshForecastsResponse(refreshed_count=0)
        except Exception as e:
            logger.exception("RefreshForecasts failed: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return weather_pb2.RefreshForecastsResponse(refreshed_count=0)
