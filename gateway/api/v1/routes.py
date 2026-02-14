"""REST routes: weather, users, cities, forecast, dress-advice (protected via AuthService)."""

import logging
from datetime import date as date_type

from fastapi import APIRouter, Depends, Query

logger = logging.getLogger(__name__)

from gateway.api.v1.schemas.cities import AddCityBody, CityResponse, ListCitiesResponse
from gateway.api.v1.schemas.dress_advice import DressAdviceResponse
from gateway.api.v1.schemas.weather import CurrentWeatherResponse, ForecastResponse
from gateway.application.use_cases.cities import AddCityUseCase, ListUserCitiesUseCase
from gateway.application.use_cases.dress_advice import GetDressAdviceForUserCityUseCase
from gateway.application.use_cases.forecast import GetForecastForUserCityUseCase
from gateway.config.settings import Settings

router = APIRouter(prefix="/api/v1", tags=["api"])

ALLOWED_FORECAST_FIELDS = {"temperature", "humidity", "wind_speed", "precipitation", "time"}


from gateway.deps import get_settings


@router.get("/users/{user_id}/cities", response_model=ListCitiesResponse)
async def list_cities(
    user_id: int,
    settings: Settings = Depends(get_settings),
):
    uc = ListUserCitiesUseCase(settings.users_grpc_addr)
    result = await uc.run(user_id)
    logger.info("list_cities user_id=%s count=%s", user_id, len(result.cities))
    return ListCitiesResponse(
        cities=[
            CityResponse(id=c.id, user_id=c.user_id, name=c.name, lat=c.lat, lon=c.lon)
            for c in result.cities
        ]
    )


@router.post("/users/{user_id}/cities", response_model=CityResponse)
async def add_city(
    user_id: int,
    body: AddCityBody,
    settings: Settings = Depends(get_settings),
):
    uc = AddCityUseCase(settings.users_grpc_addr)
    result = await uc.run(user_id, body.name, body.lat, body.lon)
    logger.info("add_city user_id=%s name=%s id=%s", user_id, body.name, result.id)
    return CityResponse(
        id=result.id,
        user_id=result.user_id,
        name=result.name,
        lat=result.lat,
        lon=result.lon,
    )


@router.get(
    "/forecast",
    response_model=ForecastResponse,
    response_model_exclude_none=True,
    summary="Forecast by city and time",
    description="Returns weather for the given city on the given day at the given time. "
    "Use `fields` to request only specific parameters: temperature, humidity, wind_speed, precipitation, time.",
)
async def get_forecast(
    user_id: int,
    city_name: str,
    time: str = Query(
        "", description="Time (e.g. 12:00 or 14:30). Required for forecast at specific time."
    ),
    date: str = Query("", description="Date ISO (YYYY-MM-DD). Empty = today"),
    fields: str | None = Query(
        None,
        description="Comma-separated: temperature, humidity, wind_speed, precipitation, time. Omit = all.",
    ),
    settings: Settings = Depends(get_settings),
):
    if not date:
        date = date_type.today().isoformat()
    uc = GetForecastForUserCityUseCase(settings.users_grpc_addr, settings.weather_grpc_addr)
    result = await uc.run(user_id, city_name, date, time)
    d = result.data
    if fields is not None and fields.strip():
        requested = {f.strip().lower() for f in fields.split(",") if f.strip()}
        requested &= ALLOWED_FORECAST_FIELDS
    else:
        requested = ALLOWED_FORECAST_FIELDS
    data = CurrentWeatherResponse()
    if "temperature" in requested:
        data.temperature = d.temperature
    if "humidity" in requested:
        data.humidity = d.humidity
    if "wind_speed" in requested:
        data.wind_speed = d.wind_speed
    if "precipitation" in requested:
        data.precipitation = d.precipitation
    if "time" in requested:
        data.time = d.time or ""
    logger.info("get_forecast user_id=%s city_name=%s date=%s", user_id, city_name, date)
    return ForecastResponse(data=data)


@router.get("/dress-advice", response_model=DressAdviceResponse)
async def get_dress_advice(
    user_id: int,
    city_name: str,
    date: str = "",
    time: str = "",
    locale: str = "en",
    settings: Settings = Depends(get_settings),
):
    uc = GetDressAdviceForUserCityUseCase(
        settings.users_grpc_addr,
        settings.weather_grpc_addr,
        settings.dress_advice_grpc_addr,
    )
    result = await uc.run(user_id, city_name, date, time, locale)
    logger.info("get_dress_advice user_id=%s city_name=%s locale=%s", user_id, city_name, locale)
    return DressAdviceResponse(advice_text=result.advice_text)
