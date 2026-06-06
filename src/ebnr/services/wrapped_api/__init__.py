import httpx
from cachetools import TTLCache

from ebnr.core.api import raw
from ebnr.services.wrapped_api.semaphore import get_semaphore
from ebnr.utils import run_with_semaphore

from . import song

__all__ = ["song", "is_vip"]

is_vip_cache = TTLCache[str, bool](maxsize=1, ttl=60 * 60 * 24)


async def is_vip() -> bool:
    if (value := is_vip_cache.get("is_vip")) is not None:
        return value
    try:
        data = await run_with_semaphore(raw.user.get_user_info(), get_semaphore())
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
