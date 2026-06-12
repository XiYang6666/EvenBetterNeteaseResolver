import httpx

from ebnr.services.wrapped_api.globals import ebnr_client
from ebnr.utils.ttl_value import AsyncTTLValue

from . import song

__all__ = ["song", "is_vip"]


async def is_vip_loader() -> bool:
    try:
        data = await ebnr_client.value.raw.user.get_user_info()
    except httpx.RequestError:
        return False
    else:
        return (
            data["code"] == 200
            and (account := data.get("account")) is not None
            and account.get("vipType", 0) > 0
        )


cached_is_vip = AsyncTTLValue(is_vip_loader, 60 * 60 * 24)


async def is_vip() -> bool:
    return await cached_is_vip.get()
