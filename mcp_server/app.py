"""McpApplication: FastMCP with registered tools."""

import logging

from mcp.server.fastmcp import FastMCP

from mcp_server.tools.handlers import DressCastToolHandlers

logger = logging.getLogger(__name__)


class McpApplication:
    def __init__(self, handlers: DressCastToolHandlers):
        self._handlers = handlers
        self._mcp = FastMCP("DressCast")

    def _register_tools(self) -> None:
        logger.debug("Registering MCP tools")

        @self._mcp.tool()
        async def get_forecast(user_id: int, city_name: str, date: str = "", time: str = "") -> str:
            return await self._handlers.get_forecast(user_id, city_name, date, time)

        @self._mcp.tool()
        async def get_dress_advice(
            user_id: int, city_name: str, date: str = "", time: str = "", locale: str = "en"
        ) -> str:
            return await self._handlers.get_dress_advice(user_id, city_name, date, time, locale)

        @self._mcp.tool()
        async def list_cities(user_id: int) -> str:
            return await self._handlers.list_cities(user_id)

        @self._mcp.tool()
        async def add_city(user_id: int, name: str, lat: float, lon: float) -> str:
            return await self._handlers.add_city(user_id, name, lat, lon)

    def run(self, transport: str = "stdio") -> None:
        self._register_tools()
        logger.info("MCP server run transport=%s", transport)
        if transport == "stdio":
            self._mcp.run(transport="stdio")
