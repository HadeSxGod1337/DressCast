"""RetryPolicy: execute_with_retry, is_retryable, backoff."""

import asyncio
import logging

logger = logging.getLogger(__name__)


def is_retryable(e: Exception) -> bool:
    import grpc

    if isinstance(e, grpc.RpcError):
        return e.code() in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.RESOURCE_EXHAUSTED)
    return False


class RetryPolicy:
    def __init__(self, max_retries: int = 3, backoff_seconds: float = 2.0):
        self._max_retries = max_retries
        self._backoff = backoff_seconds

    async def execute_with_retry(self, coro, *args, **kwargs):
        last = None
        for attempt in range(self._max_retries):
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                last = e
                if not is_retryable(e) or attempt == self._max_retries - 1:
                    raise
                delay = self._backoff * (attempt + 1)
                logger.warning(
                    "Retry %s/%s after %ss: %s", attempt + 1, self._max_retries, delay, e
                )
                await asyncio.sleep(delay)
        raise last
