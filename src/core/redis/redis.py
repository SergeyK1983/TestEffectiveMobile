from enum import StrEnum

from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError, AuthenticationError, TimeoutError, ResponseError, RedisError

from src.core.logger import logger
from src.core.config import settings


APP_USER = "application"


class RedisUserScope(StrEnum):
    cache = "cache:"
    refresh = "auth:refresh:"
    queue = "queue:"


def connect_init() -> Redis:
    client_redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        username=APP_USER,
        password=settings.redis_pass,
        decode_responses=True,
        socket_timeout=2,
        socket_connect_timeout=2,
        retry_on_timeout=True,
    )
    return client_redis


async def check_redis_client(client_redis: Redis) -> None:
    try:
        await client_redis.ping()
    except (AuthenticationError, ConnectionError, TimeoutError, ResponseError) as exp:
        logger.error("Ошибка инициализации Redis: {}", str(exp))
    except RedisError as exp:
        logger.error("RedisError ошибка инициализации Redis: {}", str(exp))
    return
