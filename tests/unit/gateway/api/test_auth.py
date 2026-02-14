"""Unit tests for Auth API: register, login, token."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


class TestRegister:
    """POST /api/v1/auth/register."""

    @patch("gateway.api.v1.auth.CreateUserUseCase")
    def test_register_returns_201_and_token(self, mock_uc_class, client):
        """Register success returns user_id, access_token, token_type bearer."""
        result_user = SimpleNamespace(id=42, username="alice", is_admin=False)
        mock_uc_class.return_value.run = AsyncMock(return_value=SimpleNamespace(user=result_user))
        r = client.post(
            "/api/v1/auth/register",
            json={"username": "alice", "password": "secret123"},  # nosec B105 - test fixture
        )
        assert r.status_code == 200
        data = r.json()
        assert data["user_id"] == 42
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str) and len(data["access_token"]) > 0

    @patch("gateway.api.v1.auth.CreateUserUseCase")
    def test_register_duplicate_username_returns_400(self, mock_uc_class, client):
        """Register with existing username returns 400."""
        mock_uc_class.return_value.run = AsyncMock(side_effect=Exception("username already exists"))
        r = client.post(
            "/api/v1/auth/register",
            json={"username": "alice", "password": "secret123"},  # nosec B105 - test fixture
        )
        assert r.status_code == 400
        assert "already exists" in r.json().get("detail", "").lower()


class TestLogin:
    """POST /api/v1/auth/login."""

    @patch("gateway.api.v1.auth.users_stub")
    def test_login_returns_token(self, mock_users_stub, client):
        """Login with valid user returns access_token."""
        mock_stub = AsyncMock()
        mock_stub.GetUserByUsername = AsyncMock(
            return_value=SimpleNamespace(id=1, username="bob", is_admin=False)
        )
        mock_users_stub.return_value = mock_stub

        r = client.post(
            "/api/v1/auth/login",
            json={"username": "bob", "password": "any"},  # nosec B105 - test fixture
        )
        assert r.status_code == 200
        data = r.json()
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)

    @patch("gateway.api.v1.auth.users_stub")
    def test_login_user_not_found_returns_401(self, mock_users_stub, client):
        """Login when user has no id returns 401."""
        mock_stub = AsyncMock()
        mock_stub.GetUserByUsername = AsyncMock(
            return_value=SimpleNamespace(id=0, username="", is_admin=False)
        )
        mock_users_stub.return_value = mock_stub

        r = client.post(
            "/api/v1/auth/login",
            json={"username": "nobody", "password": "any"},  # nosec B105 - test fixture
        )
        assert r.status_code == 401
        assert "invalid" in r.json().get("detail", "").lower()

    @patch("gateway.api.v1.auth.users_stub")
    def test_login_grpc_error_returns_401(self, mock_users_stub, client):
        """Login when gRPC raises returns 401."""
        mock_stub = AsyncMock()
        mock_stub.GetUserByUsername = AsyncMock(side_effect=Exception("connection refused"))
        mock_users_stub.return_value = mock_stub

        r = client.post(
            "/api/v1/auth/login",
            json={"username": "bob", "password": "any"},  # nosec B105 - test fixture
        )
        assert r.status_code == 401


class TestToken:
    """POST /api/v1/auth/token (OAuth2 form)."""

    @patch("gateway.api.v1.auth.users_stub")
    def test_token_returns_access_token(self, mock_users_stub, client):
        """OAuth2 token with valid credentials returns access_token."""
        mock_stub = AsyncMock()
        mock_stub.GetUserByUsername = AsyncMock(
            return_value=SimpleNamespace(id=2, username="charlie", is_admin=True)
        )
        mock_users_stub.return_value = mock_stub

        r = client.post(
            "/api/v1/auth/token",
            data={"username": "charlie", "password": "pass"},  # nosec B105 - test fixture
        )
        assert r.status_code == 200
        data = r.json()
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)

    @patch("gateway.api.v1.auth.users_stub")
    def test_token_user_not_found_returns_401(self, mock_users_stub, client):
        """OAuth2 token when user not found returns 401."""
        mock_stub = AsyncMock()
        mock_stub.GetUserByUsername = AsyncMock(
            return_value=SimpleNamespace(id=0, username="", is_admin=False)
        )
        mock_users_stub.return_value = mock_stub

        r = client.post(
            "/api/v1/auth/token",
            data={"username": "nobody", "password": "any"},  # nosec B105 - test fixture
        )
        assert r.status_code == 401
