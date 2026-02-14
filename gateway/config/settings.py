"""Gateway settings (pydantic-settings)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GATEWAY_", env_file=".env", extra="ignore")

    weather_grpc_addr: str = "localhost:50051"
    dress_advice_grpc_addr: str = "localhost:50052"
    users_grpc_addr: str = "localhost:50053"
    http_host: str = "0.0.0.0"  # nosec B104 - default for dev; override via env in prod
    http_port: int = 8000
    grpc_host: str = "0.0.0.0"  # nosec B104 - default for dev; override via env in prod
    grpc_port: int = 50050
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 1 day
    log_level: str = "INFO"
