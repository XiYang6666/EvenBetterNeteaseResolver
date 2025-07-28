from typing import Optional

from httpx import Cookies

from ebnr.core.api import raw
from ebnr.core.types import QrcodeStatus, UserShort


async def create_qrcode_uinkey() -> Optional[str]:
    data = await raw.auth.create_qrcode_unikey()
    return data["unikey"] if data["code"] == 200 else None


async def check_qrcode_satsus(
    unikey: str,
) -> tuple[QrcodeStatus, None | UserShort | Cookies | str]:
    response = await raw.auth.check_qrcode_satsus(unikey)
    data = response.json()
    if data["code"] == 801:
        return QrcodeStatus.WAITING, None
    elif data["code"] == 802:
        return QrcodeStatus.AUTHORIZING, UserShort(
            nickname=data["nickname"],
            avatar_url=data["avatarUrl"],
        )
    elif data["code"] == 803:
        return QrcodeStatus.AUTHORIZED, response.cookies
    elif data["code"] == 8821:
        return QrcodeStatus.NEED_CAPTCHA, data["redirectUrl"]
    else:
        raise ValueError(f"Unknown code: {data['code']}")

