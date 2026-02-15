import asyncio
from dataclasses import dataclass
from typing import Optional

import httpx
from cachetools import TTLCache

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
from ebnr.core.utils import extract_playlist_tracks, with_semaphore


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


size = get_config().cache_size
timeout = get_config().cache_timeout
audio_timeout = get_config().audio_cache_timeout

audio_cache = TTLCache[AudioCacheKey, AudioInfo](maxsize=size, ttl=audio_timeout)
song_cache = TTLCache[int, SongInfo](maxsize=size, ttl=timeout)
lyric_cache = TTLCache[int, LyricData](maxsize=size, ttl=timeout)
search_cache = TTLCache[SearchCacheKey, list[SongInfo]](maxsize=size, ttl=timeout)
playlist_cache = TTLCache[int, Playlist](maxsize=size, ttl=timeout)
album_cache = TTLCache[int, Album](maxsize=size, ttl=timeout)


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.FLAC,
) -> list[AudioInfo | None]:
    if get_config().audio_cache_timeout == 0 or not get_config().api_cache:
        return await song.get_audio(ids, quality, encoding)

    client = httpx.AsyncClient()

    @with_semaphore(get_config().api_semaphore)
    async def verify_url(url: str):
        response = await client.get(url)
        return response.status_code == 200

    async def verify_cache(song_id: int):
        key = AudioCacheKey(song_id, quality, encoding)
        data = audio_cache.get(AudioCacheKey(song_id, quality, encoding))
        if (
            get_config().audio_cache_type == "pessimistic"
            and data
            and data.url
            and not await verify_url(data.url)
        ):  # 悲观缓存且校验失效
            audio_cache.pop(key)
            return AudioInactive(song_id)
        elif data:
            return data
        else:
            return AudioInactive(song_id)

    verify_cache_tasks = [verify_cache(song_id) for song_id in ids]
    read_cache_result: list[AudioInfo | AudioInactive] = await asyncio.gather(
        *verify_cache_tasks
    )
    await client.aclose()

    inactive_ids = [x.id for x in read_cache_result if isinstance(x, AudioInactive)]
    inactive_map = dict(
        zip(inactive_ids, await song.get_audio(inactive_ids, quality, encoding))
    )

    for song_id, audio_data in inactive_map.items():
        if audio_data is None:
            continue
        key = AudioCacheKey(song_id, quality, encoding)
        audio_cache[key] = audio_data

    return [
        inactive_map[x.id] if isinstance(x, AudioInactive) else x
        for x in read_cache_result
    ]


async def get_song_info(ids: list[int]) -> list[SongInfo | None]:
    if not get_config().api_cache:
        return await song.get_song_info(ids)

    read_cache_result = []
    for song_id in ids:
        if data := song_cache.get(song_id):
            read_cache_result.append(data)
        else:
            read_cache_result.append(SongInactive(song_id))

    inactive_ids = [x.id for x in read_cache_result if isinstance(x, SongInactive)]
    inactive_map = dict(zip(inactive_ids, await song.get_song_info(inactive_ids)))

    for song_id, song_data in inactive_map.items():
        if song_data is None:
            continue
        song_cache[song_id] = song_data

    return [
        inactive_map[x.id] if isinstance(x, SongInactive) else x
        for x in read_cache_result
    ]


async def get_lyric(id: int) -> LyricData:
    if not get_config().api_cache:
        return await song.get_lyric(id)
    return data if (data := lyric_cache.get(id)) else await song.get_lyric(id)


async def search(keyword: str, limit: int = 10) -> list[SongInfo]:
    if not get_config().api_cache:
        return await song.search(keyword, limit)

    key = SearchCacheKey(keyword, limit)
    if data := search_cache.get(key):
        return data
    else:
        result = await song.search(keyword, limit)
        search_cache[key] = result
        return result


async def get_playlist(id: int) -> Optional[Playlist]:
    if not get_config().api_cache:
        return await song.get_playlist(id)
    return data if (data := playlist_cache.get(id)) else await song.get_playlist(id)


async def get_tracks(
    id: int, limit: int = 1000, page: int = 0
) -> Optional[list[SongInfo | None]]:
    if not get_config().api_cache:
        return await song.get_tracks(id, limit, page)

    data = playlist_cache.get(id) or await song.get_playlist(id)
    if data is None:
        return

    extracted = extract_playlist_tracks(data.track_ids, data.tracks, limit, page)
    return extracted.known + (await get_song_info(extracted.unknown))


async def get_album(id: int) -> Optional[Album]:
    if not get_config().api_cache:
        return await song.get_album(id)
    return data if (data := album_cache.get(id)) else await song.get_album(id)
