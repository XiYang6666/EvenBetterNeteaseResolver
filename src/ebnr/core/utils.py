import re
import ssl
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Literal, Optional, Protocol

import httpx

from ebnr.core.types import SongInfo

USER_AGENTS = {
    "pc": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
    "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "linux": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
}

type DeviceType = Literal["pc", "mobile", "linux"]

ssl_context = ssl.create_default_context()


def make_client(
    cookies: Optional[dict[str, str]] = None, *, device_type: DeviceType = "pc"
):
    return httpx.AsyncClient(
        verify=ssl_context,
        headers={
            "User-Agent": USER_AGENTS[device_type],
            "Referer": "https://music.163.com",
        },
        cookies=cookies,
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
        known_tracks[begin_id:end_id],
        id_list[max(begin_id, len(known_tracks)) : end_id],
    )
