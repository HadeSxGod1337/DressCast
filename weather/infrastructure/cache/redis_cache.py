"""Redis cache for weather (ForecastCache)."""

import json
import logging

import redis.asyncio as redis

from weather.application.use_cases.get_forecast import WeatherData

logger = logging.getLogger(__name__)


class RedisForecastCache:
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        self._url = redis_url
        self._ttl = default_ttl
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self._url, decode_responses=True)
        return self._client

    async def get(self, key: str) -> WeatherData | None:
        try:
            client = await self._get_client()
            raw = await client.get(key)
            if raw is None:
                return None
            j = json.loads(raw)
            return WeatherData(
                temperature=j["temperature"],
                humidity=j["humidity"],
                wind_speed=j["wind_speed"],
                precipitation=j["precipitation"],
                time=j.get("time", ""),
            )
        except Exception:
            return None

    async def set(self, key: str, data: WeatherData, ttl_seconds: int | None = None) -> None:
        try:
            client = await self._get_client()
            payload = json.dumps(
                {
                    "temperature": data.temperature,
                    "humidity": data.humidity,
                    "wind_speed": data.wind_speed,
                    "precipitation": data.precipitation,
                    "time": data.time,
                }
            )
            await client.set(key, payload, ex=ttl_seconds or self._ttl)
        except Exception as e:
            logger.warning("Redis forecast cache set failed key=%s: %s", key, e)
