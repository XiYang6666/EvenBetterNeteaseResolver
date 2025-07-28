import asyncio
from typing import Any, Callable, Coroutine


def with_semaphone(semaphone: asyncio.Semaphore):
    def decorator[T](
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        async def wrapper(*args, **kwargs):
            async with semaphone:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
