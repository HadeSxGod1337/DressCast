"""Users service settings (pydantic-settings)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="USERS_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://dresscast:dresscast@localhost:5432/dresscast"
    grpc_host: str = "0.0.0.0"  # nosec B104 - default for dev; override via env in prod
    grpc_port: int = 50053
    create_admin_username: str | None = None
    log_level: str = "INFO"
