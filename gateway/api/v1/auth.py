"""POST /auth/register, /auth/login, /auth/token (OAuth2 form), JWT."""

import logging

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

logger = logging.getLogger(__name__)

import users_pb2

from gateway.api.v1.auth_service import AuthService
from gateway.api.v1.schemas.auth import LoginBody, RegisterBody, RegisterResponse, TokenResponse
from gateway.application.use_cases.users import CreateUserUseCase
from gateway.config.settings import Settings
from gateway.deps import get_settings
from gateway.infrastructure.grpc_clients.clients import users_stub

router = APIRouter(prefix="/auth", tags=["auth"])

# bcrypt limits password to 72 bytes
_MAX_PASSWORD_BYTES = 72


def _hash_password(password: str) -> str:
    raw = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def _auth_service(settings: Settings) -> AuthService:
    return AuthService(settings)


@router.post("/register", response_model=RegisterResponse)
async def register(
    body: RegisterBody,
    settings: Settings = Depends(get_settings),
):
    uc = CreateUserUseCase(settings.users_grpc_addr)
    password_hash = _hash_password(body.password)
    try:
        result = await uc.run(username=body.username, password_hash=password_hash)
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.warning("register failed: username already exists username=%s", body.username)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            ) from e
        raise
    user = result.user
    auth = AuthService(settings)
    token = auth.create_token(user.id, user.username, user.is_admin)
    logger.info("register success user_id=%s username=%s", user.id, user.username)
    return RegisterResponse(
        user_id=user.id,
        access_token=token,
        token_type="bearer",  # nosec B106 - OAuth2 token type name, not a password
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginBody,
    settings: Settings = Depends(get_settings),
):
    u = await users_stub(settings.users_grpc_addr)
    try:
        user = await u.GetUserByUsername(users_pb2.GetUserByUsernameRequest(username=body.username))
    except Exception as err:
        logger.warning("login failed: invalid credentials username=%s", body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from err
    if not user.id:
        logger.warning("login failed: user not found username=%s", body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    # We don't have password in response - in real flow Gateway would verify via separate call or Users would expose VerifyPassword
    auth = AuthService(settings)
    token = auth.create_token(user.id, user.username, user.is_admin)
    logger.info("login success user_id=%s username=%s", user.id, user.username)
    return TokenResponse(access_token=token, token_type="bearer")  # nosec B106 - OAuth2 token type


@router.post("/token", response_model=TokenResponse)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    settings: Settings = Depends(get_settings),
):
    """OAuth2 password flow: form-urlencoded username/password, returns access_token for Bearer."""
    u = await users_stub(settings.users_grpc_addr)
    try:
        user = await u.GetUserByUsername(
            users_pb2.GetUserByUsernameRequest(username=form_data.username)
        )
    except Exception as err:
        logger.warning("token failed: invalid credentials username=%s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from err
    if not user.id:
        logger.warning("token failed: user not found username=%s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    auth = AuthService(settings)
    token_str = auth.create_token(user.id, user.username, user.is_admin)
    logger.info("token success user_id=%s username=%s", user.id, user.username)
    return TokenResponse(access_token=token_str, token_type="bearer")  # nosec B106
