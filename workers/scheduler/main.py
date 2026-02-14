"""Scheduler worker entry point (composition root)."""

import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

from workers.scheduler.clients import RefreshClients
from workers.scheduler.config import SchedulerConfig
from workers.scheduler.job import RefreshForecastsJob
from workers.scheduler.loop import ForecastRefreshScheduler
from workers.scheduler.retry import RetryPolicy


def main() -> None:
    config = SchedulerConfig()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    clients = RefreshClients(config.users_grpc_addr, config.weather_grpc_addr)
    job = RefreshForecastsJob(clients)
    retry_policy = RetryPolicy(config.max_retries, config.retry_backoff_seconds)
    scheduler = ForecastRefreshScheduler(
        job, retry_policy, config.interval_seconds, config.startup_delay_seconds
    )
    asyncio.run(scheduler.run())


if __name__ == "__main__":
    main()
