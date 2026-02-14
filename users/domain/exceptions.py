"""Domain exceptions with error codes."""

from shared.error_codes import (
    CITY_ALREADY_EXISTS,
    CITY_NOT_FOUND,
    INVALID_CREDENTIALS,
    USER_ALREADY_EXISTS,
    USER_NOT_FOUND,
)


class DomainError(Exception):
    def __init__(self, code: str, message: str = ""):
        self.code = code
        self.message = message
        super().__init__(message or code)


class UserNotFoundError(DomainError):
    def __init__(self, message: str = "User not found"):
        super().__init__(USER_NOT_FOUND, message)


class UserAlreadyExistsError(DomainError):
    def __init__(self, message: str = "User already exists"):
        super().__init__(USER_ALREADY_EXISTS, message)


class CityNotFoundError(DomainError):
    def __init__(self, message: str = "City not found"):
        super().__init__(CITY_NOT_FOUND, message)


class CityAlreadyExistsError(DomainError):
    def __init__(self, message: str = "City already exists"):
        super().__init__(CITY_ALREADY_EXISTS, message)


class InvalidCredentialsError(DomainError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(INVALID_CREDENTIALS, message)
