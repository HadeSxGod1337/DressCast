"""ForecastRefreshScheduler: loop retry(job) + sleep(interval)."""

import asyncio
import logging

from workers.scheduler.job import RefreshForecastsJob
from workers.scheduler.retry import RetryPolicy

logger = logging.getLogger(__name__)


class ForecastRefreshScheduler:
    def __init__(
        self,
        job: RefreshForecastsJob,
        retry_policy: RetryPolicy,
        interval_seconds: int,
        startup_delay_seconds: float = 0,
    ):
        self._job = job
        self._retry = retry_policy
        self._interval = interval_seconds
        self._startup_delay = startup_delay_seconds

    async def run(self) -> None:
        if self._startup_delay > 0:
            logger.info("Scheduler waiting %.0fs for backends to start", self._startup_delay)
            await asyncio.sleep(self._startup_delay)
        while True:
            try:
                await self._retry.execute_with_retry(self._job.run)
            except Exception as e:
                logger.exception("Scheduler run failed: %s", e)
            await asyncio.sleep(self._interval)
