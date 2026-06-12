import os
from contextlib import asynccontextmanager
from dataclasses import fields, is_dataclass
from typing import Any, TypeAlias, cast

from redis.asyncio import BlockingConnectionPool, Redis

from ebnr.config import get_config
from ebnr.services.async_resource import register_lazy_resource
from ebnr.services.cache.base_cache import BaseCache
from ebnr.services.cache.memory_cache import MemoryCache
from ebnr.services.cache.redis_cache import RedisCache
from ebnr.utils.lazy import Lazy


@asynccontextmanager
async def empty_context_manager():
    yield


@register_lazy_resource
@Lazy
def redis_client():
    if get_config().cache_backend != "redis":
        return cast(Redis, empty_context_manager())
    if os.getenv("VERCEL") == "1":
        redis_url = os.environ.get("REDIS_URL")
        assert redis_url
        pool = BlockingConnectionPool.from_url(redis_url)
    else:
        config = get_config().redis
        pool = BlockingConnectionPool(
            host=config.host,
            port=config.port,
            db=config.db,
            username=config.username,
            password=config.password,
            max_connections=config.max_connections,
            timeout=20,
            decode_responses=False,
        )
    client = Redis(connection_pool=pool)
    return client


async def test_cache():
    if get_config().cache_backend != "redis":
        return
    await redis_client.value.ping()


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
            redis_client.value,
            get_config().redis.prefix,
            serializer,
        )
    else:
        assert False
