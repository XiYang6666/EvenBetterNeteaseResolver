import re
import urllib.parse
from dataclasses import dataclass
from typing import Literal, Optional, cast

import httpx
from cachetools import TTLCache

from ebnr.core.api import raw

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


@dataclass
class NeteaseLinkInfo:
    url: str
    type: Literal["song", "album", "playlist"]
    id: int


def parse_netease_link(
    link: str, query_id: Optional[int] = None
) -> Optional[NeteaseLinkInfo]:
    url = urllib.parse.urlparse(link)
    # 检查 scheme
    if url.scheme not in ["", "http", "https"]:
        return None

    # 处理无 scheme
    if url.scheme == "" and url.netloc == "":
        correct_host = (matched := re.match(r"^(?:y\.)?music.163.com(/.*)$", url.path))
        path = matched and matched.group(1)
    else:
        correct_host = re.match(r"^(?:y\.)?music.163.com$", url.netloc)
        path = url.path

    # 检查 host
    if not correct_host:
        return None

    # 检查 path
    path_regex = r"^(?:/m)?/(song|album|playlist)(?:/([0-9]+))?$"
    if path is None or not (path_matched := re.match(path_regex, path)):
        return None

    # 检查 id
    # query_id 或 link 的 query 只能有一个
    query_id_from_link = (
        int(query_id_ls[0])
        if (query_id_ls := urllib.parse.parse_qs(url.query).get("id"))
        else None
    )
    if (query_id is not None) and (query_id_from_link is not None):
        return None
    query_id = query_id or query_id_from_link
    path_id = int(path_id_str) if (path_id_str := path_matched.group(2)) else None
    # id 只能有一个
    if (query_id is not None) == (path_id is not None):
        return None
    # 获取数据
    url = link if query_id is None else f"{link}?id={query_id}"
    type = path_matched.group(1)
    id = query_id or path_id
    assert type in ("song", "album", "playlist")
    assert id is not None

    return NeteaseLinkInfo(url, type, id)


async def streaming_request(method: str, url: str, chunk_size: int = 1024):
    response: Optional[httpx.Response] = None

    async def data_generator():
        nonlocal response
        async with httpx.AsyncClient() as client:
            async with client.stream(method, url) as res:
                response = res
                async for chunk in res.aiter_bytes(chunk_size=chunk_size):
                    yield chunk

    generator = data_generator()
    return cast(httpx.Response, response), generator
