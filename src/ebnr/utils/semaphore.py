import inspect
from asyncio import Semaphore
from functools import wraps
from typing import Coroutine


def with_semaphore(sem: Semaphore):
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("with_semaphore_async can only decorate async functions")

        @wraps(func)
        async def wrapper(*args, **kwargs):
            await sem.acquire()
            try:
                return await func(*args, **kwargs)
            finally:
                sem.release()

        return wrapper

    return decorator


async def run_with_semaphore[T](coroutine: Coroutine[None, None, T], sem: Semaphore):
    async with sem:
        return await coroutine
