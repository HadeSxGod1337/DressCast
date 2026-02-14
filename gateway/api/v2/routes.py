"""REST API v2: all endpoints require Bearer token; user from JWT, no user_id in URL."""

import logging
from datetime import date as date_type

import grpc
from fastapi import APIRouter, Depends, HTTPException, Query, status

from gateway.api.v1.auth_service import CurrentUser
from gateway.api.v1.errors import CITY_NOT_FOUND, message_for_code
from gateway.api.v1.schemas.cities import AddCityBody, CityResponse, ListCitiesResponse
from gateway.api.v1.schemas.dress_advice import DressAdviceResponse
from gateway.api.v1.schemas.users import UserResponse
from gateway.api.v1.schemas.weather import CurrentWeatherResponse, ForecastResponse
from gateway.application.use_cases.cities import (
    AddCityUseCase,
    GetCityUseCase,
    ListUserCitiesUseCase,
)
from gateway.application.use_cases.dress_advice import GetDressAdviceForUserCityUseCase
from gateway.application.use_cases.forecast import GetForecastForUserCityUseCase
from gateway.application.use_cases.users import GetUserByIdUseCase
from gateway.config.settings import Settings
from gateway.deps import get_current_user, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["api-v2"])

ALLOWED_FORECAST_FIELDS = {"temperature", "humidity", "wind_speed", "precipitation", "time"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    uc = GetUserByIdUseCase(settings.users_grpc_addr)
    user = await uc.run(current_user.user_id)
    logger.info("v2 get_me user_id=%s", current_user.user_id)
    return UserResponse(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        locale=user.locale or "en",
    )


@router.get("/cities/{city_name}", response_model=CityResponse)
async def get_city(
    city_name: str,
    current_user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    uc = GetCityUseCase(settings.users_grpc_addr)
    try:
        city = await uc.run(current_user.user_id, city_name)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message_for_code(CITY_NOT_FOUND),
            ) from e
        raise
    logger.info("v2 get_city user_id=%s city_name=%s", current_user.user_id, city_name)
    return CityResponse(
        id=city.id,
        user_id=city.user_id,
        name=city.name,
        lat=city.lat,
        lon=city.lon,
    )


@router.get("/cities", response_model=ListCitiesResponse)
async def list_cities(
    current_user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    uc = ListUserCitiesUseCase(settings.users_grpc_addr)
    result = await uc.run(current_user.user_id)
    logger.info("v2 list_cities user_id=%s count=%s", current_user.user_id, len(result.cities))
    return ListCitiesResponse(
        cities=[
            CityResponse(id=c.id, user_id=c.user_id, name=c.name, lat=c.lat, lon=c.lon)
            for c in result.cities
        ]
    )


@router.post("/cities", response_model=CityResponse)
async def add_city(
    body: AddCityBody,
    current_user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    uc = AddCityUseCase(settings.users_grpc_addr)
    result = await uc.run(current_user.user_id, body.name, body.lat, body.lon)
    logger.info("v2 add_city user_id=%s name=%s id=%s", current_user.user_id, body.name, result.id)
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
    city_name: str,
    current_user: CurrentUser = Depends(get_current_user),
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
    result = await uc.run(current_user.user_id, city_name, date, time)
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
    logger.info(
        "v2 get_forecast user_id=%s city_name=%s date=%s", current_user.user_id, city_name, date
    )
    return ForecastResponse(data=data)


@router.get("/dress-advice", response_model=DressAdviceResponse)
async def get_dress_advice(
    city_name: str,
    current_user: CurrentUser = Depends(get_current_user),
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
    result = await uc.run(current_user.user_id, city_name, date, time, locale)
    logger.info(
        "v2 get_dress_advice user_id=%s city_name=%s locale=%s",
        current_user.user_id,
        city_name,
        locale,
    )
    return DressAdviceResponse(advice_text=result.advice_text)
