import inspect
import re
import time
import urllib.parse
from asyncio import Semaphore
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Coroutine, Literal, Optional, TypeGuard

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


def with_semaphore(sem: Semaphore):
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
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


async def run_with_semaphore[T](coroutine: Coroutine[None, None, T], sem: Semaphore):
    async with sem:
        return await coroutine


class AutoRefreshValue[T]:
    _SENTINEL = object()

    def __init__(self, loader: Callable[[], T], ttl_seconds: float):
        self.loader = loader
        self.ttl = ttl_seconds
        self._value: T | object = AutoRefreshValue._SENTINEL
        self._expires_at: float = 0

    @classmethod
    def _check(cls, value: T | object) -> TypeGuard[T]:
        return value is not cls._SENTINEL

    def get(self) -> T:
        now = time.monotonic()
        if now > self._expires_at:
            self._value = self.loader()
            self._expires_at = now + self.ttl
        assert AutoRefreshValue._check(self._value)
        return self._value


class AsyncAutoRefreshValue[T]:
    _SENTINEL = object()

    def __init__(
        self, loader: Callable[[], Coroutine[None, None, T]], ttl_seconds: float
    ):
        self.loader = loader
        self.ttl = ttl_seconds
        self._value: T | object = AsyncAutoRefreshValue._SENTINEL
        self._expires_at: float = 0

    @classmethod
    def _check(cls, value: T | object) -> TypeGuard[T]:
        return value is not cls._SENTINEL

    async def get(self) -> T:
        now = time.time()
        if now > self._expires_at:
            self._value = await self.loader()
            self._expires_at = now + self.ttl
        assert AsyncAutoRefreshValue._check(self._value)
        return self._value
