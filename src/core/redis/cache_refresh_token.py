import socket
from datetime import timedelta

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, ResponseError, TimeoutError

from src.core.config import settings
from src.core.logger import logger
from src.core.redis.redis import RedisUserScope


async def set_cache_refresh_token(cln: Redis, username: str, token: str) -> None:
    key: str = RedisUserScope.refresh + username
    ex = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
    try:
        await cln.set(key, token, ex=ex)
    except (ConnectionError, ResponseError, TimeoutError, socket.error) as e:
        logger.error("Ошибка записи в Redis: {}", str(e))
    return


async def get_cache_refresh_token(cln: Redis, username: str) -> str:
    key: str = RedisUserScope.refresh + username
    try:
        result = await cln.get(key)
    except (ConnectionError, ResponseError, TimeoutError, socket.error) as e:
        logger.error("Ошибка чтения записи Redis: {}", str(e))
    else:
        if result is not None:
            return result
    return ""


async def delete_cache_refresh_token(cln: Redis, username: str) -> None:
    key: str = RedisUserScope.refresh + username
    try:
        await cln.delete(key)
    except (ConnectionError, ResponseError, TimeoutError, socket.error) as e:
        logger.error("Ошибка удаления записи Redis: {}", str(e))
    return
