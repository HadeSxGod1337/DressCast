"""Telegram bot config."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramBotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    gateway_grpc_addr: str = "localhost:50050"
    log_level: str = "INFO"
