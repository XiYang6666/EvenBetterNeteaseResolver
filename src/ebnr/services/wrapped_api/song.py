import asyncio
import ssl
from dataclasses import dataclass
from typing import Optional

from ebnr.config import get_config
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
from ebnr.services.wrapped_api.globals import api_semaphore, ebnr_client, http_client
from ebnr.utils.lazy import Lazy
from ebnr.utils.semaphore import with_semaphore


@dataclass(frozen=True)
class AudioCacheKey:
    id: int
    quality: Quality = Quality.STANDARD
    encoding: Encoding = Encoding.FLAC


@dataclass(frozen=True)
class SearchCacheKey:
    keyword: str
    limit: int


ssl_context = ssl.create_default_context()

size = Lazy(lambda: get_config().cache_size)
timeout = Lazy(lambda: get_config().cache_timeout)
audio_timeout = Lazy(lambda: get_config().audio_cache_timeout)

audio_cache: Lazy[BaseCache[AudioCacheKey, AudioInfo]] = Lazy(
    lambda: make_cache(maxsize=size.value, ttl=audio_timeout.value)
)
song_cache: Lazy[BaseCache[int, SongInfo]] = Lazy(
    lambda: make_cache(maxsize=size.value, ttl=timeout.value)
)
lyric_cache: Lazy[BaseCache[int, LyricData]] = Lazy(
    lambda: make_cache(maxsize=size.value, ttl=timeout.value)
)
search_cache: Lazy[BaseCache[SearchCacheKey, list[SongInfo]]] = Lazy(
    lambda: make_cache(maxsize=size.value, ttl=timeout.value)
)
playlist_cache: Lazy[BaseCache[int, Playlist]] = Lazy(
    lambda: make_cache(maxsize=size.value, ttl=timeout.value)
)
album_cache: Lazy[BaseCache[int, Album]] = Lazy(
    lambda: make_cache(maxsize=size.value, ttl=timeout.value)
)


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.FLAC,
) -> list[AudioInfo | None]:
    if get_config().audio_cache_timeout == 0 or not get_config().api_cache:
        await ebnr_client.value.song.get_audio(ids, quality, encoding)

    keys = [AudioCacheKey(song_id, quality, encoding) for song_id in ids]

    @with_semaphore(api_semaphore.value)
    async def verify_url(url: str):
        response = await http_client.get(url)
        return response.status_code == 200

    async def background_verify_url_task(url: str, key: AudioCacheKey):
        if not await verify_url(url):
            await audio_cache.value.delete(key)

    async def verify_data(data: Optional[AudioInfo], key: AudioCacheKey):
        if data is None or data.url is None:
            return False
        if get_config().audio_cache_validation_type == "sync" and not await verify_url(
            data.url
        ):
            await audio_cache.value.delete(key)
            return False
        elif get_config().audio_cache_validation_type == "sync":
            return True
        else:
            asyncio.create_task(background_verify_url_task(data.url, key))
            return True

    # read cache
    read_cache_result = await audio_cache.value.mget(keys)

    # verify data
    verify_data_tasks = [
        verify_data(data, keys[i]) for i, data in enumerate(read_cache_result)
    ]
    verify_data_result = await asyncio.gather(*verify_data_tasks)

    # retry inactive
    inactive_ids = [
        song_id for i, song_id in enumerate(ids) if not verify_data_result[i]
    ]
    inactive_retry_map = dict(
        zip(
            inactive_ids,
            await ebnr_client.value.song.get_audio(inactive_ids, quality, encoding),
        )
    )

    # update retry cache
    mset_data = {
        keys[i]: data
        for i, data in enumerate(inactive_retry_map.values())
        if data is not None
    }
    await audio_cache.value.mset(mset_data)

    # merge data
    return [
        inactive_retry_map[song_id]
        if song_id in inactive_retry_map
        else read_cache_result[i]
        for i, song_id in enumerate(ids)
    ]


async def get_song_info(ids: list[int]) -> list[SongInfo | None]:
    if not get_config().api_cache:
        return await ebnr_client.value.song.get_song_info(ids)

    read_cache_result = await song_cache.value.mget(ids)

    cache_miss_ids = [
        song_id for i, song_id in enumerate(ids) if read_cache_result[i] is None
    ]
    fetched = await ebnr_client.value.song.get_song_info(cache_miss_ids)
    inactive_map = dict(zip(cache_miss_ids, fetched))

    mset_data = {
        song_id: data for song_id, data in inactive_map.items() if data is not None
    }
    if mset_data:
        await song_cache.value.mset(mset_data)

    return [
        inactive_map.get(song_id, read_cache_result[i]) for i, song_id in enumerate(ids)
    ]


async def get_lyric(id: int) -> LyricData:
    if not get_config().api_cache:
        return await ebnr_client.value.song.get_lyric(id)
    return (
        data
        if (data := await lyric_cache.value.get(id))
        else await ebnr_client.value.song.get_lyric(id)
    )


async def search(keyword: str, limit: int = 10) -> list[SongInfo]:
    if not get_config().api_cache:
        return await ebnr_client.value.song.search(keyword, limit)

    key = SearchCacheKey(keyword, limit)
    if data := await search_cache.value.get(key):
        return data
    else:
        result = await ebnr_client.value.song.search(keyword, limit)
        await search_cache.value.set(key, result)
        return result


async def get_playlist(id: int) -> Optional[Playlist]:
    if not get_config().api_cache:
        return await ebnr_client.value.song.get_playlist(id)
    return (
        data
        if (data := await playlist_cache.value.get(id))
        else await ebnr_client.value.song.get_playlist(id)
    )


async def get_tracks(
    id: int, limit: int = 1000, page: int = 0
) -> Optional[list[SongInfo | None]]:
    if not get_config().api_cache:
        return await ebnr_client.value.song.get_tracks(id, limit, page)

    if (
        data := (await playlist_cache.value.get(id))
        or await ebnr_client.value.song.get_playlist(id)
    ) is None:
        return

    extracted = extract_playlist_tracks(data.track_ids, data.tracks, limit, page)
    return extracted.known + (await get_song_info(extracted.unknown))


async def get_album(id: int) -> Optional[Album]:
    if not get_config().api_cache:
        return await ebnr_client.value.song.get_album(id)
    return (
        data
        if (data := await album_cache.value.get(id))
        else await ebnr_client.value.song.get_album(id)
    )
