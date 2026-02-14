"""Dress Advice service entry point (composition root)."""

import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import dress_advice_pb2_grpc
from grpc import aio

from dress_advice.api.servicer import DressAdviceServicer
from dress_advice.application.use_cases.get_advice import GetAdviceUseCase
from dress_advice.config.settings import Settings
from dress_advice.infrastructure.cache.redis_cache import RedisAdviceCache
from dress_advice.infrastructure.external.openai_provider import OpenAIAdviceProvider

logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    provider = OpenAIAdviceProvider(
        api_key=settings.openai_api_key,
        proxy=settings.openai_http_proxy,
    )

    try:
        cache = RedisAdviceCache(settings.redis_url)
    except Exception:
        cache = None
        logger.warning("Redis unavailable, running without cache")
    get_advice_uc = GetAdviceUseCase(provider, cache)
    servicer = DressAdviceServicer(get_advice_uc)

    async def serve() -> None:
        server = aio.server()
        dress_advice_pb2_grpc.add_DressAdviceServiceServicer_to_server(servicer, server)
        server.add_insecure_port(f"{settings.grpc_host}:{settings.grpc_port}")
        await server.start()
        logger.info(
            "Dress Advice gRPC server listening on %s:%s", settings.grpc_host, settings.grpc_port
        )
        await server.wait_for_termination()

    asyncio.run(serve())


if __name__ == "__main__":
    main()
