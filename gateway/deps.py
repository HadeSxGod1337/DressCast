"""FastAPI dependencies: Settings, AuthService, get_current_user."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from gateway.api.v1.auth_service import AuthService, CurrentUser
from gateway.config.settings import Settings

# Path used by Swagger UI for OAuth2 password flow (login/password form)
OAUTH2_TOKEN_URL = "/api/v1/auth/token"  # nosec B105 - URL path, not a password


def get_settings() -> Settings:
    return Settings()


def get_auth_service(settings: Settings = Depends(get_settings)) -> AuthService:
    return AuthService(settings)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=OAUTH2_TOKEN_URL, auto_error=True)


def get_current_user(
    auth: AuthService = Depends(get_auth_service),
    token: str = Depends(oauth2_scheme),
) -> CurrentUser:
    return auth.decode_token(token)
