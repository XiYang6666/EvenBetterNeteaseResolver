import re
import urllib.parse
from datetime import datetime
from typing import Literal, Optional, Protocol, Sequence

import httpx

from ebnr.core.cookie import get_cookies

COOKIES = {
    "pc": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
    "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "linux": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
}

type DeviceType = Literal["pc", "mobile", "linux"]


def make_client(*, with_cookie: bool = True, device_type: DeviceType = "pc"):
    return httpx.AsyncClient(
        headers={
            "User-Agent": COOKIES[device_type],
            "Referer": "https://music.163.com",
        },
        cookies={
            **get_cookies(),
            "__remember_me": "true",
            "os": "pc",
        }
        if with_cookie
        else None,
    )


def fix_song_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc
    assert host is not None, "Invalid URL"
    new_host = re.sub(
        r"^m([78])04\.music\.126\.net$",
        lambda m: f"m{m.group(1)}01.music.126.net",
        host,
    )
    result = parsed._replace(scheme="https", netloc=new_host).geturl()
    return result


def make_datetime(ts: float):
    try:
        return datetime.fromtimestamp(ts)
    except OSError:
        return None


class HaveId(Protocol):
    id: int


def remap_result[T: HaveId](ids: list[int], list: Sequence[T]) -> list[Optional[T]]:
    id_map = {i.id: i for i in list}
    return [id_map.get(i) for i in ids]
