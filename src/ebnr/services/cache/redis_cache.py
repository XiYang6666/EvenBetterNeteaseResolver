import pickle
from typing import Callable, Optional, overload

from redis.asyncio import Redis

from ebnr.services.cache.base_cache import BaseCache


class RedisCache[K, V](BaseCache[K, V]):
    REDIS_RAW_MODE_ERROR_MSG = "Redis instance should be configured with decode_responses=False (keep raw data mode)"

    def __init__(
        self,
        ttl: float,
        client: Redis,
        prefix: str,
        serializer: Callable[[K], str],
    ):
        if ttl < 0:
            raise ValueError("ttl must be non-negative")
        if client.get_connection_kwargs().get("decode_responses", False):
            raise ValueError(RedisCache.REDIS_RAW_MODE_ERROR_MSG)

        self._ttl = ttl
        self._client = client
        self._prefix = prefix
        self._serializer = serializer

    @property
    def ttl(self) -> float:
        return self._ttl

    def _make_key(self, key: K) -> str:
        return f"{self._prefix}{self._serializer(key)}"

    def _resolve_ttl(self, ttl: float | None) -> float:
        return self._ttl if ttl is None else ttl

    @overload
    async def get(self, key: K, default: V) -> V: ...
    @overload
    async def get(self, key: K, default: None = None) -> V | None: ...

    async def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        raw = await self._client.get(self._make_key(key))
        assert not isinstance(raw, str), RedisCache.REDIS_RAW_MODE_ERROR_MSG
        if raw is None:
            return default
        return pickle.loads(raw)

    async def set(self, key: K, value: V, ttl: float | None = None) -> None:
        resolved = self._resolve_ttl(ttl)
        raw = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        if resolved > 0:
            await self._client.set(self._make_key(key), raw, px=int(resolved * 1000))
        else:
            await self._client.set(self._make_key(key), raw)  # 永不过期

    async def delete(self, key: K) -> bool:
        return await self._client.delete(self._make_key(key)) > 0

    async def exists(self, key: K) -> bool:
        return await self._client.exists(self._make_key(key)) > 0
