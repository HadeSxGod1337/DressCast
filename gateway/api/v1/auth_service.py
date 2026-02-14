"""AuthService: JWT create/verify, get_current_user. AccessPolicy: require_admin, require_same_user_or_admin."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gateway.config.settings import Settings


@dataclass
class CurrentUser:
    user_id: int
    username: str
    is_admin: bool


class AuthService:
    def __init__(self, settings: Settings):
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._expire_minutes = settings.jwt_expire_minutes

    def create_token(self, user_id: int, username: str, is_admin: bool) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "username": username,
            "is_admin": is_admin,
            "iat": now,
            "exp": now + timedelta(minutes=self._expire_minutes),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, token: str) -> CurrentUser:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return CurrentUser(
                user_id=int(payload["sub"]),
                username=payload["username"],
                is_admin=payload.get("is_admin", False),
            )
        except (jwt.InvalidTokenError, KeyError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from e

    def get_current_user(
        self,
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(HTTPBearer(auto_error=False)),
        ],
    ) -> CurrentUser:
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        return self.decode_token(credentials.credentials)

    def require_admin(self, current_user: CurrentUser) -> None:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin required",
            )

    def require_same_user_or_admin(self, current_user: CurrentUser, resource_user_id: int) -> None:
        if current_user.is_admin:
            return
        if current_user.user_id != resource_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )


def get_auth_service(settings: Settings) -> AuthService:
    return AuthService(settings)


# For FastAPI Depends(): dependency that provides AuthService
def get_auth(settings: Settings) -> AuthService:
    return AuthService(settings)
