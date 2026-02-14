"""Domain entities (optional separate from ORM)."""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    password_hash: str | None
    telegram_id: str | None
    is_admin: bool
    locale: str


@dataclass
class City:
    id: int
    user_id: int
    name: str
    lat: float
    lon: float
