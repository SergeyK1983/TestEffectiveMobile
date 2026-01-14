import json
import socket
from datetime import datetime, date
from uuid import UUID
from functools import wraps
from typing import Callable, Any

from fastapi.encoders import jsonable_encoder
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError, ResponseError, TimeoutError
from sqlalchemy import RowMapping

from src.core.redis.redis import RedisUserScope, redis_user_ctx
from src.core.logger import logger


class AppRedisClient:
    redis_client: Redis = None


app_redis = AppRedisClient()


def set_redis_client_cache(cln: Redis) -> None:
    app_redis.redis_client = cln
    return None


def default_serializer(obj: Any):
    if isinstance(obj, UUID):
        return jsonable_encoder(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, RowMapping):
        return dict(obj)
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if not hasattr(obj, "__dict__"):
        return obj
    raise TypeError(f"Cannot serialize {type(obj)}")


def set_and_get_cache(ttl: int = 60, key: str = None):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            username = redis_user_ctx.get()

            if ttl and not isinstance(ttl, int):
                raise TypeError("Срок действия ключа redis (arg: 'ttl') должен быть типом int")
            if key and not isinstance(key, str):
                raise TypeError("Наименование ключа redis (arg: 'key') должно быть типом str")

            ex: int = ttl
            rc = app_redis.redis_client
            if rc is None:
                logger.error("set_and_get_cache - Отсутствует подключение к клиенту Redis: {}", str(rc))
                result = await func(*args, **kwargs)
                return result

            for_key = []
            if username:
                for_key.append(username)

            for_key.append(func.__name__)

            if args:
                if hasattr(args[0], "__dict__"):
                    for_key.append(args[0].__class__.__name__)
                else:
                    if isinstance(args[0], (str, int, float, bool)):
                        for_key.append(args[0])
            if kwargs:
                value = list(kwargs.values())[0]
                if isinstance(value, (str, int, float, bool)):
                    for_key.append(value)

            cache_key = RedisUserScope.cache
            if key:
                cache_key += f"{key}_"

            cache_key += "_".join(for_key)

            try:
                result = await rc.get(cache_key)
            except (ConnectionError, ResponseError, TimeoutError, socket.error) as e:
                logger.error("Ошибка чтения Redis: {}", str(e))
            else:
                if result is not None:
                    return json.loads(result)

            result = await func(*args, **kwargs)

            if result and cache_key:
                try:
                    payload = json.dumps(result, default=default_serializer)
                except TypeError as e:
                    logger.error("Ошибка при попытке собрать json для Redis: {}", str(e))
                    return result
                try:
                    await rc.set(name=cache_key, value=payload, ex=ex, nx=True)
                except (ConnectionError, ResponseError, TimeoutError, socket.error) as e:
                    logger.error("Ошибка записи в Redis: {}", str(e))

            return result
        return wrapper
    return decorator


def async_set_get_cache(
        func: Callable = None,
        *,
        ttl: int = 60,
        key: str = None,
):
    """
    Декоратор Шредингера. Наименование ключа (key) будет добавлено к сформированному наименованию,
    e.g.: cache:key_autokey. Записи сохраняются в области Redis "cache:".
    Args:
        func: func
        ttl: Время жизни записи, по умолчанию 60с
        key: Наименование ключа
    """
    decorator = set_and_get_cache(ttl, key)
    if func is None:
        return decorator
    else:
        return decorator(func)
