"""gRPC servicer: delegates to use case, maps exceptions."""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import dress_advice_pb2
import dress_advice_pb2_grpc
import grpc

from dress_advice.api.errors import domain_error_to_grpc
from dress_advice.application.use_cases.get_advice import WeatherData
from dress_advice.domain.exceptions import DomainError

logger = logging.getLogger(__name__)


def _request_to_weather_data(request) -> WeatherData:
    w = request.weather_data
    return WeatherData(
        temperature=w.temperature,
        humidity=w.humidity,
        wind_speed=w.wind_speed,
        precipitation=w.precipitation,
        time=w.time or "",
    )


class DressAdviceServicer(dress_advice_pb2_grpc.DressAdviceServiceServicer):
    def __init__(self, get_advice_uc):
        self._get_advice = get_advice_uc

    async def GetAdvice(self, request, context):
        locale = request.locale or "en"
        logger.info("GetAdvice locale=%s", locale)
        try:
            wd = _request_to_weather_data(request)
            text = await self._get_advice.run(wd, locale)
            return dress_advice_pb2.GetAdviceResponse(advice_text=text)
        except DomainError as e:
            code, msg = domain_error_to_grpc(e)
            logger.warning("GetAdvice DomainError locale=%s code=%s", locale, getattr(e, "code", e))
            context.set_code(code)
            context.set_details(msg)
            return dress_advice_pb2.GetAdviceResponse(advice_text="")
        except Exception as e:
            logger.exception("GetAdvice failed locale=%s: %s", locale, e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dress_advice_pb2.GetAdviceResponse(advice_text="")
