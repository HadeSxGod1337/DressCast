"""CreateUser, GetUserById, GetOrCreateUserByTelegramId via Users stub."""

import users_pb2

from gateway.infrastructure.grpc_clients.clients import users_stub


class GetUserByIdUseCase:
    def __init__(self, users_address: str):
        self._users_addr = users_address

    async def run(self, user_id: int):
        u = await users_stub(self._users_addr)
        return await u.GetUserById(users_pb2.GetUserByIdRequest(user_id=user_id))


class CreateUserUseCase:
    def __init__(self, users_address: str):
        self._users_addr = users_address

    async def run(self, username: str, password_hash: str):
        u = await users_stub(self._users_addr)
        return await u.CreateUser(
            users_pb2.CreateUserRequest(username=username, password_hash=password_hash)
        )


class GetOrCreateUserByTelegramIdUseCase:
    def __init__(self, users_address: str):
        self._users_addr = users_address

    async def run(self, telegram_id: str, username: str = "", locale: str = "en"):
        u = await users_stub(self._users_addr)
        return await u.GetOrCreateUserByTelegramId(
            users_pb2.GetOrCreateUserByTelegramIdRequest(
                telegram_id=telegram_id,
                username=username or "",
                locale=locale,
            )
        )
