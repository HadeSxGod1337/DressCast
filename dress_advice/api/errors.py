"""Map domain exceptions to gRPC status."""

import grpc

from dress_advice.domain.exceptions import DomainError


def domain_error_to_grpc(exc: DomainError) -> tuple[grpc.StatusCode, str]:
    code = exc.code
    msg = exc.message or code
    if code == "VALIDATION_ERROR":
        return grpc.StatusCode.INVALID_ARGUMENT, msg
    if code == "SERVICE_UNAVAILABLE":
        return grpc.StatusCode.UNAVAILABLE, msg
    if code == "ADVICE_PROVIDER_NOT_CONFIGURED":
        return grpc.StatusCode.FAILED_PRECONDITION, msg
    return grpc.StatusCode.UNKNOWN, msg
