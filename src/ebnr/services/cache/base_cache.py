from abc import ABC, abstractmethod
from typing import Mapping, Optional, Sequence, overload


class BaseCache[K, V](ABC):
    @property
    @abstractmethod
    def ttl(self) -> float: ...

    @overload
    async def get(self, key: K, default: V) -> V: ...

    @overload
    async def get(self, key: K, default: None = None) -> Optional[V]: ...

    @abstractmethod
    async def get(self, key: K, default: Optional[V] = None) -> Optional[V]: ...

    @abstractmethod
    async def set(self, key: K, value: V, ttl: Optional[int] = None): ...

    @abstractmethod
    async def delete(self, key: K) -> bool: ...

    @abstractmethod
    async def exists(self, key: K) -> bool: ...

    @overload
    async def mget(self, keys: Sequence[K], default: V) -> Sequence[V]: ...

    @overload
    async def mget(
        self, keys: Sequence[K], default: None = None
    ) -> Sequence[Optional[V]]: ...

    @abstractmethod
    async def mget(
        self, keys: Sequence[K], default: Optional[V] = None
    ) -> Sequence[Optional[V]]: ...

    @abstractmethod
    async def mset(self, mapping: Mapping[K, V], ttl: Optional[int] = None): ...
