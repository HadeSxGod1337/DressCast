"""Cities schemas."""

from pydantic import BaseModel


class CityResponse(BaseModel):
    id: int
    user_id: int
    name: str
    lat: float
    lon: float


class AddCityBody(BaseModel):
    name: str
    lat: float
    lon: float


class ListCitiesResponse(BaseModel):
    cities: list[CityResponse]
