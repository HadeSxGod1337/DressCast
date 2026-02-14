"""McpConfig from env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class McpConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    gateway_grpc_addr: str = "localhost:50050"
    log_level: str = "INFO"
