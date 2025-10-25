import asyncio
import re
import urllib.parse
from asyncio import Semaphore
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Iterable, Literal, Optional, Protocol

import httpx

from ebnr.core.cookie import get_cookies
from ebnr.core.types import SongInfo

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


def remap_result[T: HaveId](ids: list[int], list: Iterable[T]) -> list[Optional[T]]:
    id_map = {i.id: i for i in list}
    return [id_map.get(i) for i in ids]


def with_semaphore(sem: Semaphore):
    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
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


@dataclass
class ExtractedTracks:
    known: list[SongInfo]
    unknown: list[int]


def extract_playlist_tracks(
    all_id: list[int],
    known_tracks: list[SongInfo],
    limit: int = 1000,
    page: int = 0,
):
    begin_id = page * limit
    end_id = page * limit + limit
    id_list: list[int] = all_id[begin_id:end_id]
    return ExtractedTracks(
        known_tracks[begin_id:end_id], id_list[max(begin_id, 1000) : end_id]
    )
