"""Map domain exceptions to gRPC status."""

import grpc

from weather.domain.exceptions import DomainError


def domain_error_to_grpc(exc: DomainError) -> tuple[grpc.StatusCode, str]:
    code = exc.code
    msg = exc.message or code
    if code == "VALIDATION_ERROR":
        return grpc.StatusCode.INVALID_ARGUMENT, msg
    if code == "SERVICE_UNAVAILABLE":
        return grpc.StatusCode.UNAVAILABLE, msg
    return grpc.StatusCode.UNKNOWN, msg
