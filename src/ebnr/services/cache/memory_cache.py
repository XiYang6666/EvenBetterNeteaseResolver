import time
from collections import OrderedDict
from typing import Optional, cast, overload

from ebnr.services.cache.base_cache import BaseCache


class MemoryCache[K, V](BaseCache[K, V]):
    _SENTINEL = object()

    def __init__(self, maxsize: int, ttl: float) -> None:
        if maxsize <= 0:
            raise ValueError("size must be positive")
        if ttl < 0:
            raise ValueError("ttl must be non-negative")
        self._maxsize = maxsize
        self._ttl = ttl
        self._cache: OrderedDict[K, tuple[V, float | None]] = OrderedDict()

    @property
    def maxsize(self) -> int:
        return self._maxsize

    @property
    def ttl(self) -> float:
        return self._ttl

    def _expire_at(self, ttl: float | None) -> float | None:
        resolved = self._ttl if ttl is None else ttl
        return None if resolved == 0 else time.monotonic() + resolved

    def _is_expired(self, expire_at: float | None) -> bool:
        return expire_at is not None and time.monotonic() > expire_at

    def _evict_expired(self) -> None:
        expired = [k for k, (_, exp) in self._cache.items() if self._is_expired(exp)]
        for k in expired:
            del self._cache[k]

    def _evict_lru(self) -> None:
        self._cache.popitem(last=False)

    @overload
    async def get(self, key: K, default: V) -> V: ...
    @overload
    async def get(self, key: K, default: None = None) -> V | None: ...

    async def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        entry = self._cache.get(key, MemoryCache._SENTINEL)
        if entry is MemoryCache._SENTINEL:
            return default
        value, expire_at = cast(tuple[V, float], entry)
        if self._is_expired(expire_at):
            del self._cache[key]
            return default
        self._cache.move_to_end(key)
        return value

    async def set(self, key: K, value: V, ttl: float | None = None) -> None:
        self._evict_expired()
        if key in self._cache:
            self._cache.move_to_end(key)
        elif len(self._cache) >= self._maxsize:
            self._evict_lru()
        self._cache[key] = (value, self._expire_at(ttl))

    async def delete(self, key: K) -> bool:
        if key not in self._cache:
            return False
        del self._cache[key]
        return True

    async def exists(self, key: K) -> bool:
        return self._cache.get(key, MemoryCache._SENTINEL) is not MemoryCache._SENTINEL
