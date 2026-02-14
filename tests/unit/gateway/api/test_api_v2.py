"""Unit tests for API v2: me, cities, forecast, dress-advice (Bearer auth)."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import grpc


class _FakeRpcError(grpc.RpcError, Exception):
    """Minimal RpcError for testing 404 handling."""

    def code(self):
        return grpc.StatusCode.NOT_FOUND

    def details(self):
        return "not found"


class TestMe:
    """GET /api/v2/me."""

    @patch("gateway.api.v2.routes.GetUserByIdUseCase")
    def test_me_returns_current_user(self, mock_uc_class, v2_client):
        """Returns user profile for authenticated user."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(id=1, username="testuser", is_admin=False, locale="en")
        )
        r = v2_client.get("/api/v2/me")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == 1
        assert data["username"] == "testuser"
        assert data["is_admin"] is False
        assert data.get("locale", "en") == "en"

    @patch("gateway.api.v2.routes.GetUserByIdUseCase")
    def test_me_without_token_returns_401(self, _mock_uc_class, app):
        """Without Bearer token returns 401."""
        from fastapi.testclient import TestClient

        # No override: real get_current_user will require token
        client = TestClient(app)
        r = client.get("/api/v2/me")
        assert r.status_code == 401


class TestGetCity:
    """GET /api/v2/cities/{city_name}."""

    @patch("gateway.api.v2.routes.GetCityUseCase")
    def test_get_city_returns_city(self, mock_uc_class, v2_client):
        """Returns city by name for current user."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(id=5, user_id=1, name="Moscow", lat=55.75, lon=37.62)
        )
        r = v2_client.get("/api/v2/cities/Moscow")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == 5
        assert data["name"] == "Moscow"
        assert data["lat"] == 55.75

    @patch("gateway.api.v2.routes.GetCityUseCase")
    def test_get_city_not_found_returns_404(self, mock_uc_class, v2_client):
        """City not found returns 404."""
        mock_uc_class.return_value.run = AsyncMock(side_effect=_FakeRpcError())
        r = v2_client.get("/api/v2/cities/UnknownCity")
        assert r.status_code == 404


class TestListCitiesV2:
    """GET /api/v2/cities."""

    @patch("gateway.api.v2.routes.ListUserCitiesUseCase")
    def test_list_cities_returns_cities(self, mock_uc_class, v2_client):
        """Returns cities for current user from JWT."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(
                cities=[
                    SimpleNamespace(id=1, user_id=1, name="Moscow", lat=55.75, lon=37.62),
                ]
            )
        )
        r = v2_client.get("/api/v2/cities")
        assert r.status_code == 200
        assert len(r.json()["cities"]) == 1
        assert r.json()["cities"][0]["name"] == "Moscow"


class TestAddCityV2:
    """POST /api/v2/cities."""

    @patch("gateway.api.v2.routes.AddCityUseCase")
    def test_add_city_returns_created_city(self, mock_uc_class, v2_client):
        """Add city for current user."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(id=10, user_id=1, name="Kazan", lat=55.79, lon=49.12)
        )
        r = v2_client.post(
            "/api/v2/cities",
            json={"name": "Kazan", "lat": 55.79, "lon": 49.12},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Kazan"
        assert data["user_id"] == 1


class TestForecastV2:
    """GET /api/v2/forecast."""

    @patch("gateway.api.v2.routes.GetForecastForUserCityUseCase")
    def test_forecast_returns_data(self, mock_uc_class, v2_client):
        """Forecast for user's city returns weather data."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(
                data=SimpleNamespace(
                    temperature=18.0,
                    humidity=60.0,
                    wind_speed=2.0,
                    precipitation=0.0,
                    time="12:00",
                )
            )
        )
        r = v2_client.get("/api/v2/forecast", params={"city_name": "Moscow"})
        assert r.status_code == 200
        assert r.json()["data"]["temperature"] == 18.0


class TestDressAdviceV2:
    """GET /api/v2/dress-advice."""

    @patch("gateway.api.v2.routes.GetDressAdviceForUserCityUseCase")
    def test_dress_advice_returns_text(self, mock_uc_class, v2_client):
        """Dress advice for user's city."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(advice_text="Bring an umbrella.")
        )
        r = v2_client.get("/api/v2/dress-advice", params={"city_name": "London"})
        assert r.status_code == 200
        assert r.json()["advice_text"] == "Bring an umbrella."
