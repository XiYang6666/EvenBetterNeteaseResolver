from abc import ABC, abstractmethod
from typing import Optional, overload


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
    async def set(self, key: K, value: V, ttl: Optional[int] = None): ...

    @abstractmethod
    async def delete(self, key: K) -> bool: ...

    @abstractmethod
    async def exists(self, key: K) -> bool: ...

    