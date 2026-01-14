from typing import TYPE_CHECKING
from contextlib import asynccontextmanager

from src.core.redis.redis import connect_init, check_redis_client
from src.core.redis.cache_decorator import set_redis_client_cache

if TYPE_CHECKING:
    from fastapi import FastAPI
    from redis.asyncio.client import Redis


@asynccontextmanager
async def lifespan(app: "FastAPI"):
    client_redis: "Redis" = connect_init()
    await check_redis_client(client_redis)
    app.state.redis_client = client_redis
    set_redis_client_cache(client_redis)
    yield

    await client_redis.aclose()
