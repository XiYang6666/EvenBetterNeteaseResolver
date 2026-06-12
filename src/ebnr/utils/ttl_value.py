import time
from collections.abc import Callable
from typing import Coroutine, cast


class TTLValue[T]:
    _SENTINEL = object()

    def __init__(self, loader: Callable[[], T], ttl: float):
        self.loader = loader
        self.ttl = ttl
        self._value: T | object = TTLValue._SENTINEL
        self._expires_at: float = 0

    def get(self) -> T:
        now = time.monotonic()
        if now > self._expires_at:
            self._value = self.loader()
            self._expires_at = now + self.ttl
        return cast(T, self._value)


class AsyncTTLValue[T]:
    _SENTINEL = object()

    def __init__(self, loader: Callable[[], Coroutine[None, None, T]], ttl: float):
        self.loader = loader
        self.ttl = ttl
        self._value: T | object = AsyncTTLValue._SENTINEL
        self._expires_at: float = 0

    async def get(self) -> T:
        now = time.time()
        if now > self._expires_at:
            self._value = await self.loader()
            self._expires_at = now + self.ttl
        return cast(T, self._value)
