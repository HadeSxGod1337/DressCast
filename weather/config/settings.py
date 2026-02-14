"""Weather service settings (pydantic-settings)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEATHER_", env_file=".env", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    grpc_host: str = "0.0.0.0"  # nosec B104 - default for dev; override via env in prod
    grpc_port: int = 50051
    log_level: str = "INFO"
