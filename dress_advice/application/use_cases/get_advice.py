"""GetAdvice use case (cache-aside + AdviceProvider)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class WeatherData:
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    time: str


class AdviceProvider(Protocol):
    async def get_advice(self, weather_data: WeatherData, locale: str = "en") -> str: ...


class AdviceCache(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, text: str, ttl_seconds: int = 3600) -> None: ...


class GetAdviceUseCase:
    def __init__(self, provider: AdviceProvider, cache: AdviceCache | None = None):
        self._provider = provider
        self._cache = cache

    async def run(self, weather_data: WeatherData, locale: str = "en") -> str:
        key = f"advice:{weather_data.temperature:.1f}:{weather_data.humidity:.0f}:{weather_data.wind_speed:.1f}:{weather_data.precipitation:.1f}:{locale}"
        if self._cache:
            cached = await self._cache.get(key)
            if cached is not None:
                return cached
        text = await self._provider.get_advice(weather_data, locale)
        if self._cache:
            await self._cache.set(key, text)
        return text
