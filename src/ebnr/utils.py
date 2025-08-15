import asyncio
from typing import Any, Callable, Coroutine

import httpx
from cachetools import TTLCache

from ebnr.core.api import raw


def with_semaphore(semaphore: asyncio.Semaphore):
    def decorator[T](
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


is_vip_cache = TTLCache(maxsize=1, ttl=60 * 60 * 24)


async def is_vip() -> bool:
    if is_vip_cache.get("is_vip") is not None:
        return is_vip_cache["is_vip"]
    try:
        data = await raw.user.get_user_info()
    except httpx.RequestError:
        is_vip_cache["is_vip"] = False
        return False
    else:
        result = (
            data["code"] == 200
            and (account := data.get("account")) is not None
            and account.get("vipType", 0) > 0
        )
        is_vip_cache["is_vip"] = result
        return result
