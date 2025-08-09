import re
import urllib.parse
from typing import Optional, Protocol, Sequence

import httpx

from ebnr.core.cookie import get_cookies


def make_client(with_cookie: bool = True):
    return httpx.AsyncClient(
        headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
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


class HaveId(Protocol):
    id: int


def remap_result[T: HaveId](ids: list[int], list: Sequence[T]) -> list[Optional[T]]:
    id_map = {i.id: i for i in list}
    return [id_map.get(i) for i in ids]
