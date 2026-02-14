"""Fixtures for gateway REST API unit tests (TestClient, no gRPC lifespan)."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from gateway.api.v1.auth import router as auth_router
from gateway.api.v1.auth_service import CurrentUser
from gateway.api.v1.routes import router as api_v1_router
from gateway.api.v2.routes import router as api_v2_router
from gateway.config.settings import Settings
from gateway.deps import get_current_user, get_settings

# JWT secret >= 32 bytes to avoid PyJWT InsecureKeyLengthWarning in tests
TEST_JWT_SECRET = "test-secret-at-least-32-bytes-long-for-hmac"  # nosec B105 - test secret


@asynccontextmanager
async def _empty_lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """No-op lifespan so tests do not start gRPC server."""
    yield


def create_test_app() -> FastAPI:
    """App with same REST routes as gateway.main but without gRPC lifespan."""
    app = FastAPI(title="DressCast Gateway Test", lifespan=_empty_lifespan)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(api_v1_router)
    app.include_router(api_v2_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Use test settings with long-enough JWT secret to avoid InsecureKeyLengthWarning
    app.dependency_overrides[get_settings] = lambda: Settings(jwt_secret=TEST_JWT_SECRET)
    return app


@pytest.fixture
def app() -> FastAPI:
    """FastAPI test app (no gRPC)."""
    return create_test_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """TestClient for the test app."""
    return TestClient(app)


# Default current user for v2 tests when overriding get_current_user.
TEST_CURRENT_USER = CurrentUser(user_id=1, username="testuser", is_admin=False)


@pytest.fixture
def v2_client(app: FastAPI) -> TestClient:
    """Client with get_current_user overridden so v2 endpoints accept requests."""
    app.dependency_overrides[get_current_user] = lambda: TEST_CURRENT_USER
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
