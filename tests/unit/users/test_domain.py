"""Users domain exceptions."""

from users.domain.exceptions import CityNotFoundError, UserNotFoundError


def test_user_not_found_has_code():
    e = UserNotFoundError("no user")
    assert e.code == "USER_NOT_FOUND"
    assert "no user" in str(e)


def test_city_not_found_has_code():
    e = CityNotFoundError("no city")
    assert e.code == "CITY_NOT_FOUND"
