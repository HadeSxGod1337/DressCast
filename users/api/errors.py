"""Map domain exceptions to gRPC status."""

import grpc

from users.domain.exceptions import DomainError


def domain_error_to_grpc(exc: DomainError) -> tuple[grpc.StatusCode, str]:
    """Map domain error code to gRPC status code and message."""
    code = exc.code
    msg = exc.message or code
    if code == "USER_NOT_FOUND" or code == "CITY_NOT_FOUND":
        return grpc.StatusCode.NOT_FOUND, msg
    if code == "USER_ALREADY_EXISTS" or code == "CITY_ALREADY_EXISTS":
        return grpc.StatusCode.ALREADY_EXISTS, msg
    if code == "INVALID_CREDENTIALS":
        return grpc.StatusCode.UNAUTHENTICATED, msg
    if code == "VALIDATION_ERROR":
        return grpc.StatusCode.INVALID_ARGUMENT, msg
    return grpc.StatusCode.UNKNOWN, msg
