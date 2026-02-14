"""Weather schemas."""

from pydantic import BaseModel


# All optional so we can return only requested fields
class CurrentWeatherResponse(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    precipitation: float | None = None
    time: str | None = None


class ForecastResponse(BaseModel):
    data: CurrentWeatherResponse

    model_config = {
        "json_schema_extra": {
            "example": {"data": {"temperature": 5.2, "humidity": 80, "time": "12:00"}}
        }
    }
