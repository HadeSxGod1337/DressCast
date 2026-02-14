"""OpenAI-based advice provider (AdviceProvider)."""

import logging

from openai import AsyncOpenAI, DefaultAsyncHttpxClient

from dress_advice.application.use_cases.get_advice import AdviceProvider, WeatherData
from dress_advice.domain.exceptions import AdviceProviderNotConfiguredError

logger = logging.getLogger(__name__)


class OpenAIAdviceProvider(AdviceProvider):
    def __init__(self, api_key: str, proxy: str | None = None):
        self._api_key = (api_key or "").strip()
        if self._api_key:
            if proxy:
                http_client = DefaultAsyncHttpxClient(proxy=proxy)
                self._client = AsyncOpenAI(api_key=self._api_key, http_client=http_client)
            else:
                self._client = AsyncOpenAI(api_key=self._api_key)
        else:
            self._client = None

    async def get_advice(self, weather_data: WeatherData, locale: str = "en") -> str:
        if not self._api_key or self._client is None:
            raise AdviceProviderNotConfiguredError(
                "OpenAI API key not set; set OPENAI_API_KEY to enable dress advice."
            )
        logger.debug("OpenAI get_advice locale=%s", locale)
        prompt = (
            "You are a friendly outfit advisor. Given: "
            f"temperature {weather_data.temperature}°C, humidity {weather_data.humidity}%, "
            f"wind {weather_data.wind_speed} m/s, precipitation {weather_data.precipitation} mm. "
            f"Reply in {locale} in 1-2 short, lively sentences. "
            "Use 1-3 relevant emoji (weather/clothing, e.g. ☀️🧥☔️). Keep it concise and warm."
        )
        try:
            r = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
            return (r.choices[0].message.content or "").strip()
        except Exception as e:
            logger.exception("OpenAI get_advice failed locale=%s: %s", locale, e)
            raise
