"""GetCurrentWeather and GetForecast use cases (cache-aside + WeatherProvider)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class WeatherData:
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    time: str


class WeatherProvider(Protocol):
    async def get_current_weather(self, lat: float, lon: float) -> WeatherData: ...
    async def get_forecast(
        self, lat: float, lon: float, date: str = "", time: str = ""
    ) -> WeatherData: ...


class ForecastCache(Protocol):
    async def get(self, key: str) -> WeatherData | None: ...
    async def set(self, key: str, data: WeatherData, ttl_seconds: int = 3600) -> None: ...


class GetCurrentWeatherUseCase:
    def __init__(self, provider: WeatherProvider, cache: ForecastCache | None = None):
        self._provider = provider
        self._cache = cache

    async def run(self, lat: float, lon: float) -> WeatherData:
        key = f"current:{lat:.4f}:{lon:.4f}"
        if self._cache:
            cached = await self._cache.get(key)
            if cached is not None:
                return cached
        data = await self._provider.get_current_weather(lat, lon)
        if self._cache:
            await self._cache.set(key, data)
        return data


class GetForecastUseCase:
    def __init__(self, provider: WeatherProvider, cache: ForecastCache | None = None):
        self._provider = provider
        self._cache = cache

    async def run(self, lat: float, lon: float, date: str = "", time: str = "") -> WeatherData:
        key = f"forecast:{lat:.4f}:{lon:.4f}:{date}:{time}"
        if self._cache:
            cached = await self._cache.get(key)
            if cached is not None:
                return cached
        data = await self._provider.get_forecast(lat, lon, date, time)
        if self._cache:
            await self._cache.set(key, data)
        return data


class RefreshForecastsUseCase:
    def __init__(self, provider: WeatherProvider):
        self._provider = provider

    async def run(self, coords: list[tuple[float, float]]) -> int:
        count = 0
        for lat, lon in coords:
            try:
                await self._provider.get_current_weather(lat, lon)
                count += 1
            except Exception:  # nosec B110 - skip failed coords, count successes
                pass
        return count
