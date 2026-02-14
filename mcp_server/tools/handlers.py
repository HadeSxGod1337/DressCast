"""DressCastToolHandlers: MCP tool methods calling GatewayClient."""

import logging

from mcp_server.gateway_client import GatewayClient

logger = logging.getLogger(__name__)


class DressCastToolHandlers:
    def __init__(self, gateway_client: GatewayClient):
        self._client = gateway_client

    async def get_forecast(
        self, user_id: int, city_name: str, date: str = "", time: str = ""
    ) -> str:
        logger.info(
            "MCP get_forecast user_id=%s city_name=%s date=%s time=%s",
            user_id,
            city_name,
            date,
            time,
        )
        try:
            r = await self._client.get_forecast(user_id, city_name, date, time)
            d = r.weather_data
            return (
                f"Temperature: {d.temperature}°C, humidity: {d.humidity}%, wind: {d.wind_speed} m/s"
            )
        except Exception as e:
            logger.warning(
                "MCP get_forecast failed user_id=%s city_name=%s: %s", user_id, city_name, e
            )
            return f"Error: {e}"

    async def get_dress_advice(
        self, user_id: int, city_name: str, date: str = "", time: str = "", locale: str = "en"
    ) -> str:
        logger.info(
            "MCP get_dress_advice user_id=%s city_name=%s locale=%s", user_id, city_name, locale
        )
        try:
            r = await self._client.get_dress_advice(user_id, city_name, date, time, locale)
            return r.advice_text
        except Exception as e:
            logger.warning(
                "MCP get_dress_advice failed user_id=%s city_name=%s: %s", user_id, city_name, e
            )
            return f"Error: {e}"

    async def list_cities(self, user_id: int) -> str:
        logger.info("MCP list_cities user_id=%s", user_id)
        try:
            r = await self._client.list_cities(user_id)
            if not r.cities:
                return "No cities."
            return "\n".join(f"- {c.name} ({c.lat}, {c.lon})" for c in r.cities)
        except Exception as e:
            logger.warning("MCP list_cities failed user_id=%s: %s", user_id, e)
            return f"Error: {e}"

    async def add_city(self, user_id: int, name: str, lat: float, lon: float) -> str:
        logger.info("MCP add_city user_id=%s name=%s lat=%s lon=%s", user_id, name, lat, lon)
        try:
            await self._client.add_city(user_id, name, lat, lon)
            return f"Added city {name}."
        except Exception as e:
            logger.warning("MCP add_city failed user_id=%s name=%s: %s", user_id, name, e)
            return f"Error: {e}"
