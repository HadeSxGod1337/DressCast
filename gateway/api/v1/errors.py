"""Error codes and mapping to HTTP/gRPC."""

from dataclasses import dataclass

CITY_NOT_FOUND = "CITY_NOT_FOUND"
CITY_ALREADY_EXISTS = "CITY_ALREADY_EXISTS"
USER_NOT_FOUND = "USER_NOT_FOUND"
INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
VALIDATION_ERROR = "VALIDATION_ERROR"
SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


@dataclass
class ApiError:
    code: str
    message: str


def message_for_code(code: str, locale: str = "en") -> str:
    messages = {
        CITY_NOT_FOUND: {"en": "City not found", "ru": "Город не найден"},
        CITY_ALREADY_EXISTS: {"en": "City already exists", "ru": "Город уже добавлен"},
        USER_NOT_FOUND: {"en": "User not found", "ru": "Пользователь не найден"},
        INVALID_CREDENTIALS: {"en": "Invalid credentials", "ru": "Неверные данные"},
        VALIDATION_ERROR: {"en": "Validation error", "ru": "Ошибка проверки"},
        SERVICE_UNAVAILABLE: {"en": "Service unavailable", "ru": "Сервис недоступен"},
    }
    return messages.get(code, {}).get(locale, messages.get(code, {}).get("en", code))
