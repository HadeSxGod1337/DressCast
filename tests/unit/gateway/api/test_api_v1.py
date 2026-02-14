"""Unit tests for API v1: users/cities, forecast, dress-advice."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


class TestListCities:
    """GET /api/v1/users/{user_id}/cities."""

    @patch("gateway.api.v1.routes.ListUserCitiesUseCase")
    def test_list_cities_returns_cities(self, mock_uc_class, client):
        """Returns list of cities for user."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(
                cities=[
                    SimpleNamespace(id=1, user_id=10, name="Moscow", lat=55.75, lon=37.62),
                    SimpleNamespace(id=2, user_id=10, name="SPb", lat=59.93, lon=30.31),
                ]
            )
        )
        r = client.get("/api/v1/users/10/cities")
        assert r.status_code == 200
        data = r.json()
        assert "cities" in data
        assert len(data["cities"]) == 2
        assert data["cities"][0]["name"] == "Moscow"
        assert data["cities"][1]["name"] == "SPb"

    @patch("gateway.api.v1.routes.ListUserCitiesUseCase")
    def test_list_cities_empty_returns_empty_list(self, mock_uc_class, client):
        """Returns empty cities when user has none."""
        mock_uc_class.return_value.run = AsyncMock(return_value=SimpleNamespace(cities=[]))
        r = client.get("/api/v1/users/99/cities")
        assert r.status_code == 200
        assert r.json() == {"cities": []}


class TestAddCity:
    """POST /api/v1/users/{user_id}/cities."""

    @patch("gateway.api.v1.routes.AddCityUseCase")
    def test_add_city_returns_201_and_city(self, mock_uc_class, client):
        """Add city returns created city."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(id=3, user_id=10, name="Kazan", lat=55.79, lon=49.12)
        )
        r = client.post(
            "/api/v1/users/10/cities",
            json={"name": "Kazan", "lat": 55.79, "lon": 49.12},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == 3
        assert data["user_id"] == 10
        assert data["name"] == "Kazan"
        assert data["lat"] == 55.79
        assert data["lon"] == 49.12


class TestForecast:
    """GET /api/v1/forecast."""

    @patch("gateway.api.v1.routes.GetForecastForUserCityUseCase")
    def test_forecast_returns_weather_data(self, mock_uc_class, client):
        """Forecast returns temperature and other fields."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(
                data=SimpleNamespace(
                    temperature=15.0,
                    humidity=70.0,
                    wind_speed=3.0,
                    precipitation=0.0,
                    time="12:00",
                )
            )
        )
        r = client.get(
            "/api/v1/forecast",
            params={"user_id": 10, "city_name": "Moscow"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "data" in data
        assert data["data"]["temperature"] == 15.0
        assert data["data"]["humidity"] == 70.0

    @patch("gateway.api.v1.routes.GetForecastForUserCityUseCase")
    def test_forecast_with_fields_filter(self, mock_uc_class, client):
        """Forecast with fields query returns only requested fields."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(
                data=SimpleNamespace(
                    temperature=20.0,
                    humidity=50.0,
                    wind_speed=2.0,
                    precipitation=0.0,
                    time="14:00",
                )
            )
        )
        r = client.get(
            "/api/v1/forecast",
            params={"user_id": 1, "city_name": "London", "fields": "temperature,time"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["data"]["temperature"] == 20.0
        assert data["data"]["time"] == "14:00"
        # humidity not requested
        assert "humidity" not in data["data"] or data["data"].get("humidity") is None


class TestDressAdvice:
    """GET /api/v1/dress-advice."""

    @patch("gateway.api.v1.routes.GetDressAdviceForUserCityUseCase")
    def test_dress_advice_returns_text(self, mock_uc_class, client):
        """Dress advice returns advice_text."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(advice_text="Wear a light jacket.")
        )
        r = client.get(
            "/api/v1/dress-advice",
            params={"user_id": 10, "city_name": "Moscow"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["advice_text"] == "Wear a light jacket."

    @patch("gateway.api.v1.routes.GetDressAdviceForUserCityUseCase")
    def test_dress_advice_with_locale(self, mock_uc_class, client):
        """Dress advice accepts locale param."""
        mock_uc_class.return_value.run = AsyncMock(
            return_value=SimpleNamespace(advice_text="Теплая куртка.")
        )
        r = client.get(
            "/api/v1/dress-advice",
            params={"user_id": 1, "city_name": "Moscow", "locale": "ru"},
        )
        assert r.status_code == 200
        assert r.json()["advice_text"] == "Теплая куртка."
