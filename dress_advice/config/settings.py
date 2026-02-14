"""Dress Advice service settings (pydantic-settings)."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env next to project root (parent of dress_advice package) so it's found regardless of cwd
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DRESS_ADVICE_",
        env_file=_ENV_FILE if _ENV_FILE.exists() else None,
        extra="ignore",
    )

    redis_url: str = "redis://localhost:6379/0"
    grpc_host: str = "0.0.0.0"  # nosec B104 - default for dev; override via env in prod
    grpc_port: int = 50052
    log_level: str = "INFO"

    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_http_proxy: str | None = Field(default=None, validation_alias="OPENAI_HTTP_PROXY")
