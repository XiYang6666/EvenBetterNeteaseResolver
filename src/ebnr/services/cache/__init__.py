from dataclasses import fields, is_dataclass
from typing import Any, Optional, TypeAlias

from redis.asyncio import Redis

from ebnr.config import get_config
from ebnr.services.cache.base_cache import BaseCache
from ebnr.services.cache.memory_cache import MemoryCache
from ebnr.services.cache.redis_cache import RedisCache

redis_client: Optional[Redis] = None


def init_redis_client():
    global redis_client
    config = get_config().redis
    redis_client = Redis(
        host=config.host,
        port=config.port,
        db=config.db,
        username=config.username,
        password=config.password,
        max_connections=config.max_connections,
    )


def get_redis_client():
    assert redis_client
    return redis_client


async def check_redis_client():
    client = await get_redis_client()
    await client.ping()


def load_cache():
    if get_config().cache_backend != "redis":
        return
    init_redis_client()


async def stop_cache():
    if get_config().cache_backend != "redis":
        return
    await get_redis_client().close()


BaseTypes: TypeAlias = str | int | bool


def base_serializer(data: BaseTypes):
    assert isinstance(data, BaseTypes)
    if isinstance(data, str):
        return data
    return str(data)


def dataclass_serializer(data: Any):
    assert is_dataclass(data)
    return type(data).__name__ + ",".join(
        base_serializer(getattr(data, field.name)) for field in fields(data)
    )


def serializer(data: Any):
    if isinstance(data, BaseTypes):
        return base_serializer(data)
    elif is_dataclass(data):
        return dataclass_serializer(data)
    else:
        assert False


def make_cache[K, V](maxsize: int, ttl: float) -> BaseCache[K, V]:  # pyright: ignore[reportInvalidTypeVarUse]
    cache_backend = get_config().cache_backend

    if cache_backend == "memory":
        return MemoryCache(maxsize, ttl)
    elif cache_backend == "redis":
        return RedisCache(
            ttl,
            get_redis_client(),
            get_config().redis.prefix,
            serializer,
        )
    else:
        assert False
