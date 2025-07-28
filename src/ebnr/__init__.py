import asyncio
import os
import sys
from pathlib import Path

from qrcode import QRCode

from ebnr.app import app
from ebnr.core.api.auth import check_qrcode_satsus, create_qrcode_uinkey

__all__ = [
    "app",
    "login",
]


async def login():
    # 扫码登录需要滑块验证码验证, 目前暂时不支持滑块验证码验证
    unikey = await create_qrcode_uinkey()
    assert unikey is not None
    qrcode = QRCode()
    qrcode.add_data(f"https://music.163.com/login?codekey={unikey}")
    qrcode.make(fit=True)
    # save qrcode to file
    with open("data/qrcode.png", "wb") as f:
        qrcode.make_image(fill_color="black", back_color="white").save(f)
    # print qrcode to console
    if sys.stdout.isatty():
        qrcode.print_tty()
    else:
        qrcode.print_ascii()
    # show qrcode if possible
    if (
        sys.platform.startswith("win")
        or sys.platform.startswith("darwin")
        or (sys.platform.startswith("linux") and "DISPLAY" in os.environ)
        or (sys.platform.startswith("linux") and "WAYLAND_DISPLAY" in os.environ)
        or (sys.platform.startswith("freebsd") and "DISPLAY" in os.environ)
        or (sys.platform.startswith("freebsd") and "WAYLAND_DISPLAY" in os.environ)
    ):
        os.startfile(Path("data/qrcode.png").absolute())

    while True:
        await asyncio.sleep(3)
        cookies = await check_qrcode_satsus(unikey)
        if cookies is None:
            continue
        return cookies
