"""Auth request/response schemas."""

from pydantic import BaseModel


class RegisterBody(BaseModel):
    username: str
    password: str


class LoginBody(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user_id: int
    access_token: str
    token_type: str = "bearer"
