import asyncio
import ssl
from dataclasses import dataclass
from typing import Optional

import httpx
from lazy_object_proxy import Proxy

from ebnr.config import get_config
from ebnr.core.api import song
from ebnr.core.types import (
    Album,
    AudioInfo,
    Encoding,
    LyricData,
    Playlist,
    Quality,
    SongInfo,
)
from ebnr.core.utils import extract_playlist_tracks
from ebnr.services.cache import make_cache
from ebnr.services.cache.base_cache import BaseCache
from ebnr.services.wrapped_api.semaphore import get_semaphore
from ebnr.utils import run_with_semaphore, with_semaphore


@dataclass(frozen=True)
class AudioCacheKey:
    id: int
    quality: Quality = Quality.STANDARD
    encoding: Encoding = Encoding.FLAC


@dataclass(frozen=True)
class AudioInactive:
    id: int


@dataclass(frozen=True)
class SongInactive:
    id: int


@dataclass(frozen=True)
class SearchCacheKey:
    keyword: str
    limit: int


ssl_context = ssl.create_default_context()

size: int = Proxy(lambda: get_config().cache_size)
timeout: int = Proxy(lambda: get_config().cache_timeout)
audio_timeout: int = Proxy(lambda: get_config().audio_cache_timeout)

audio_cache: BaseCache[AudioCacheKey, AudioInfo] = Proxy(
    lambda: make_cache(maxsize=size, ttl=audio_timeout)
)
song_cache: BaseCache[int, SongInfo] = Proxy(
    lambda: make_cache(maxsize=size, ttl=timeout)
)
lyric_cache: BaseCache[int, LyricData] = Proxy(
    lambda: make_cache(maxsize=size, ttl=timeout)
)
search_cache: BaseCache[SearchCacheKey, list[SongInfo]] = Proxy(
    lambda: make_cache(maxsize=size, ttl=timeout)
)
playlist_cache: BaseCache[int, Playlist] = Proxy(
    lambda: make_cache(maxsize=size, ttl=timeout)
)
album_cache: BaseCache[int, Album] = Proxy(
    lambda: make_cache(maxsize=size, ttl=timeout)
)


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.FLAC,
) -> list[AudioInfo | None]:
    if get_config().audio_cache_timeout == 0 or not get_config().api_cache:
        return await run_with_semaphore(
            song.get_audio(ids, quality, encoding), get_semaphore()
        )

    client = httpx.AsyncClient(verify=ssl_context)

    @with_semaphore(get_semaphore())
    async def verify_url(url: str):
        response = await client.get(url)
        return response.status_code == 200

    async def background_verify_url(url: str, key: AudioCacheKey):
        if await verify_url(url):
            return
        await audio_cache.delete(key)

    async def get_from_cache(song_id: int):
        key = AudioCacheKey(song_id, quality, encoding)
        data = await audio_cache.get(key)
        if not (data and data.url):
            return AudioInactive(song_id)
        if (
            get_config().audio_cache_validation_type == "sync"
            and not await verify_url(data.url)  # type: ignore
        ):
            # 同步缓存且校验失效
            await audio_cache.delete(key)
            return AudioInactive(song_id)
        elif get_config().audio_cache_validation_type == "sync":
            # 同步缓存且校验成功
            return data
        elif get_config().audio_cache_validation_type == "background":
            # 异步缓存
            asyncio.create_task(background_verify_url(data.url, key))  # type: ignore
            return data
        else:
            assert False

    read_cache_tasks = [get_from_cache(song_id) for song_id in ids]
    read_cache_result = await asyncio.gather(*read_cache_tasks)
    await client.aclose()

    inactive_ids = [x.id for x in read_cache_result if isinstance(x, AudioInactive)]
    inactive_map = dict(
        zip(inactive_ids, await song.get_audio(inactive_ids, quality, encoding))
    )

    for song_id, audio_data in inactive_map.items():
        if audio_data is None:
            continue
        key = AudioCacheKey(song_id, quality, encoding)
        await audio_cache.set(key, audio_data)

    return [
        inactive_map[x.id] if isinstance(x, AudioInactive) else x
        for x in read_cache_result
    ]


async def get_song_info(ids: list[int]) -> list[SongInfo | None]:
    if not get_config().api_cache:
        return await run_with_semaphore(song.get_song_info(ids), get_semaphore())

    async def get_from_cache(song_id: int):
        return await song_cache.get(song_id) or SongInactive(song_id)

    read_cache_tasks = [get_from_cache(song_id) for song_id in ids]
    read_cache_result = await asyncio.gather(*read_cache_tasks)

    inactive_ids = [x.id for x in read_cache_result if isinstance(x, SongInactive)]
    inactive_map = dict(zip(inactive_ids, await song.get_song_info(inactive_ids)))

    for song_id, song_data in inactive_map.items():
        if song_data is None:
            continue
        await song_cache.set(song_id, song_data)

    return [
        inactive_map[x.id] if isinstance(x, SongInactive) else x
        for x in read_cache_result
    ]


async def get_lyric(id: int) -> LyricData:
    if not get_config().api_cache:
        return await run_with_semaphore(song.get_lyric(id), get_semaphore())
    return data if (data := await lyric_cache.get(id)) else await song.get_lyric(id)


async def search(keyword: str, limit: int = 10) -> list[SongInfo]:
    if not get_config().api_cache:
        return await song.search(keyword, limit)

    key = SearchCacheKey(keyword, limit)
    if data := await search_cache.get(key):
        return data
    else:
        result = await song.search(keyword, limit)
        await search_cache.set(key, result)
        return result


async def get_playlist(id: int) -> Optional[Playlist]:
    if not get_config().api_cache:
        return await run_with_semaphore(song.get_playlist(id), get_semaphore())
    return (
        data if (data := await playlist_cache.get(id)) else await song.get_playlist(id)
    )


async def get_tracks(
    id: int, limit: int = 1000, page: int = 0
) -> Optional[list[SongInfo | None]]:
    if not get_config().api_cache:
        return await run_with_semaphore(
            song.get_tracks(id, limit, page), get_semaphore()
        )

    if (data := (await playlist_cache.get(id)) or await song.get_playlist(id)) is None:
        return

    extracted = extract_playlist_tracks(data.track_ids, data.tracks, limit, page)
    return extracted.known + (await get_song_info(extracted.unknown))


async def get_album(id: int) -> Optional[Album]:
    if not get_config().api_cache:
        return await run_with_semaphore(song.get_album(id), get_semaphore())
    return data if (data := await album_cache.get(id)) else await song.get_album(id)
