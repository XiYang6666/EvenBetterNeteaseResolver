from collections.abc import MutableSequence
from contextlib import asynccontextmanager
from typing import Any, Protocol, cast

from ebnr.utils.lazy import AsyncLazy, Lazy


class AsyncContextManagerProtocol(Protocol):
    async def __aenter__(self) -> Any: ...
    async def __aexit__(
        self, exc_type: Any, exc_value: Any, traceback: Any, /
    ) -> bool | None: ...


resources: MutableSequence[AsyncContextManagerProtocol] = []
lazy_resources: MutableSequence[Lazy[AsyncContextManagerProtocol]] = []
async_lazy_resources: MutableSequence[AsyncLazy[AsyncContextManagerProtocol]] = []


def register_resource[T: AsyncContextManagerProtocol](resource: T) -> T:
    resources.append(resource)
    return resource


def register_lazy_resource[T: AsyncContextManagerProtocol](
    resource: Lazy[T],
) -> Lazy[T]:
    lazy_resources.append(cast(Lazy[AsyncContextManagerProtocol], resource))
    return resource


def register_async_lazy_resource[T: AsyncContextManagerProtocol](
    resource: AsyncLazy[T],
) -> AsyncLazy[T]:
    async_lazy_resources.append(cast(AsyncLazy[AsyncContextManagerProtocol], resource))
    return resource


async def enter_resources():
    for resource in resources:
        await resource.__aenter__()

    for resource in lazy_resources:
        resource.get()
        await resource.value.__aenter__()

    for resource in async_lazy_resources:
        await resource.get()
        await (await resource.value).__aenter__()


async def exit_resources():
    for resource in resources:
        await resource.__aexit__(None, None, None)

    for resource in lazy_resources:
        await resource.value.__aexit__(None, None, None)

    for resource in async_lazy_resources:
        await (await resource.value).__aexit__(None, None, None)


@asynccontextmanager
async def resources_manager():
    await enter_resources()
    yield
    await exit_resources()
