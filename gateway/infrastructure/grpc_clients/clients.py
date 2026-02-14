"""gRPC stubs for Weather, DressAdvice, Users (created from pool)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

import dress_advice_pb2_grpc
import users_pb2_grpc
import weather_pb2_grpc

from gateway.infrastructure.grpc_clients.pool import get_channel


async def weather_stub(address: str) -> weather_pb2_grpc.WeatherServiceStub:
    ch = await get_channel(address)
    return weather_pb2_grpc.WeatherServiceStub(ch)


async def dress_advice_stub(address: str) -> dress_advice_pb2_grpc.DressAdviceServiceStub:
    ch = await get_channel(address)
    return dress_advice_pb2_grpc.DressAdviceServiceStub(ch)


async def users_stub(address: str) -> users_pb2_grpc.UsersServiceStub:
    ch = await get_channel(address)
    return users_pb2_grpc.UsersServiceStub(ch)
