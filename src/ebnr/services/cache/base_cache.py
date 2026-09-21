from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import overload


class BaseCache[K, V](ABC):
    @property
    @abstractmethod
    def ttl(self) -> float: ...

    @overload
    async def get(self, key: K, default: V) -> V: ...

    @overload
    async def get(self, key: K, default: None = None) -> V | None: ...

    @abstractmethod
    async def get(self, key: K, default: V | None = None) -> V | None: ...

    @abstractmethod
    async def set(self, key: K, value: V, ttl: int | None = None): ...

    @abstractmethod
    async def delete(self, key: K) -> bool: ...

    @abstractmethod
    async def exists(self, key: K) -> bool: ...

    @overload
    async def mget(self, keys: Sequence[K], default: V) -> Sequence[V]: ...

    @overload
    async def mget(
        self, keys: Sequence[K], default: None = None
    ) -> Sequence[V | None]: ...

    @abstractmethod
    async def mget(
        self, keys: Sequence[K], default: V | None = None
    ) -> Sequence[V | None]: ...

    @abstractmethod
    async def mset(self, mapping: Mapping[K, V], ttl: int | None = None): ...
