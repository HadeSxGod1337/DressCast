"""Scheduler config (env)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class SchedulerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SCHEDULER_", env_file=".env", extra="ignore")

    users_grpc_addr: str = "localhost:50053"
    weather_grpc_addr: str = "localhost:50051"
    interval_seconds: int = 900
    startup_delay_seconds: float = 15.0
    max_retries: int = 3
    retry_backoff_seconds: float = 2.0
    log_level: str = "INFO"
