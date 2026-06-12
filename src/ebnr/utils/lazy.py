from typing import Callable, Coroutine, cast, override


class Lazy[T]:
    _SENTINEL = object()

    def __init__(self, factory: Callable[[], T]) -> None:
        self.factory = factory
        self._value: T | object = VarLazy._SENTINEL

    @property
    def value(self):
        return self.get()

    def get(self) -> T:
        if self._value is self._SENTINEL:
            self._value = self.factory()
        return cast(T, self._value)


class VarLazy[T](Lazy[T]):
    def __init__(self, factory: Callable[[], T]) -> None:
        super().__init__(factory)

    @property
    @override
    def value(self) -> T:
        return super().value

    @value.setter
    def value_setter(self, value: T):
        self.set(value)

    def set(self, value: T):
        self._value = value


class AsyncLazy[T]:
    _SENTINEL = object()

    def __init__(self, factory: Callable[[], Coroutine[None, None, T]]) -> None:
        self.factory = factory
        self._value: T | object = VarLazy._SENTINEL

    @property
    async def value(self):
        return await self.get()

    async def get(self) -> T:
        if self._value is self._SENTINEL:
            self._value = await self.factory()
        return cast(T, self._value)


class VarAsyncLazy[T](AsyncLazy[T]):
    def __init__(self, factory: Callable[[], Coroutine[None, None, T]]) -> None:
        super().__init__(factory)

    @property
    @override
    async def value(self) -> T:
        return await super().value

    @value.setter
    def value_setter(self, value: T):
        self.set(value)

    def set(self, value: T):
        self._value = value
