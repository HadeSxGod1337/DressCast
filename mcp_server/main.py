"""MCP server entry point (composition root). Use: python -m mcp_server.main"""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

from mcp_server.app import McpApplication
from mcp_server.config import McpConfig
from mcp_server.gateway_client import GatewayClient
from mcp_server.tools.handlers import DressCastToolHandlers

logger = logging.getLogger(__name__)


def main() -> None:
    config = McpConfig()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logger.info("MCP server starting")
    client = GatewayClient(config.gateway_grpc_addr)
    handlers = DressCastToolHandlers(client)
    app = McpApplication(handlers)
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
