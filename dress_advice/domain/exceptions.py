"""Domain exceptions with error codes."""

from shared.error_codes import (
    ADVICE_PROVIDER_NOT_CONFIGURED,
    SERVICE_UNAVAILABLE,
    VALIDATION_ERROR,
)


class DomainError(Exception):
    def __init__(self, code: str, message: str = ""):
        self.code = code
        self.message = message
        super().__init__(message or code)


class ServiceUnavailableError(DomainError):
    def __init__(self, message: str = "Service unavailable"):
        super().__init__(SERVICE_UNAVAILABLE, message)


class ValidationError(DomainError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(VALIDATION_ERROR, message)


class AdviceProviderNotConfiguredError(DomainError):
    """Raised when OpenAI (or other advice provider) is not configured (e.g. missing API key)."""

    def __init__(self, message: str = "Advice provider not configured"):
        super().__init__(ADVICE_PROVIDER_NOT_CONFIGURED, message)
