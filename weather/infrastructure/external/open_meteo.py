"""Open-Meteo API adapter (WeatherProvider)."""

import logging

import httpx

from weather.application.use_cases.get_forecast import WeatherData, WeatherProvider

logger = logging.getLogger(__name__)


class OpenMeteoProvider(WeatherProvider):
    BASE = "https://api.open-meteo.com/v1/forecast"

    async def get_current_weather(self, lat: float, lon: float) -> WeatherData:
        logger.debug("Open-Meteo get_current_weather lat=%s lon=%s", lat, lon)
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    self.BASE,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
                    },
                    timeout=10.0,
                )
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "Open-Meteo HTTP error lat=%s lon=%s status=%s",
                    lat,
                    lon,
                    e.response.status_code,
                )
                raise
            except Exception as e:
                logger.exception("Open-Meteo request failed lat=%s lon=%s: %s", lat, lon, e)
                raise
            j = r.json()
            c = j.get("current", {})
            return WeatherData(
                temperature=float(c.get("temperature_2m", 0)),
                humidity=float(c.get("relative_humidity_2m", 0)),
                wind_speed=float(c.get("wind_speed_10m", 0)),
                precipitation=float(c.get("precipitation", 0)),
                time=c.get("time", ""),
            )

    async def get_forecast(
        self, lat: float, lon: float, date: str = "", time: str = ""
    ) -> WeatherData:
        data = await self.get_current_weather(lat, lon)
        if date:
            data = WeatherData(
                temperature=data.temperature,
                humidity=data.humidity,
                wind_speed=data.wind_speed,
                precipitation=data.precipitation,
                time=date + "T" + time if time else date,
            )
        return data
