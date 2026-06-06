import re
import urllib.parse
from dataclasses import dataclass
from typing import Callable, Literal, Optional, TypeGuard

import httpx


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
    async_client = httpx.AsyncClient()
    response = await async_client.send(httpx.Request(method, url), stream=True)

    async def data_generator():
        async for chunk in response.aiter_bytes(chunk_size=chunk_size):
            yield chunk
        await response.aclose()
        await async_client.aclose()

    return response, data_generator()


def maybe_apply[T, R](value: Optional[T], func: Callable[[T], R]) -> Optional[R]:
    if value is None:
        return None
    return func(value)


def validate_with_fallback[T, S](
    value: T, rule: Callable[[T], TypeGuard[S]], fallback: S
) -> S:
    if rule(value):
        return value
    return fallback


def first_not_none[T](
    *getters: *tuple[*tuple[Callable[[], Optional[T]], ...], Callable[[], T]],
) -> T:
    for getter in getters:
        if (value := getter()) is not None:
            return value
    else:
        assert False
