"""Channel pool by address and event loop."""

import asyncio
import logging

from grpc import aio

logger = logging.getLogger(__name__)

_channel_cache: dict[tuple[str, id], aio.Channel] = {}
_lock = asyncio.Lock()


async def get_channel(address: str) -> aio.Channel:
    loop = asyncio.get_event_loop()
    key = (address, id(loop))
    async with _lock:
        if key not in _channel_cache:
            logger.debug("gRPC channel created for address=%s", address)
            _channel_cache[key] = aio.insecure_channel(address)
        return _channel_cache[key]
