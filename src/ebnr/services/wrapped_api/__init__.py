import httpx

from ebnr.core.api import raw
from ebnr.services.wrapped_api.semaphore import get_semaphore
from ebnr.utils import AsyncAutoRefreshValue, run_with_semaphore

from . import song

__all__ = ["song", "is_vip"]


async def is_vip_loader() -> bool:
    try:
        data = await run_with_semaphore(raw.user.get_user_info(), get_semaphore())
    except httpx.RequestError:
        return False
    else:
        return (
            data["code"] == 200
            and (account := data.get("account")) is not None
            and account.get("vipType", 0) > 0
        )


cached_is_vip = AsyncAutoRefreshValue(is_vip_loader, 60 * 60 * 24)


async def is_vip() -> bool:
    return await cached_is_vip.get()
