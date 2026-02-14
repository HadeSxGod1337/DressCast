"""Users schemas."""

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    locale: str


class CreateUserResponse(BaseModel):
    user: UserResponse
