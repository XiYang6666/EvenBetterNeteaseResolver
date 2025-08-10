from typing import Any, Optional

from cachetools import Cache, LFUCache, TTLCache

from ebnr.config import get_config
from ebnr.core.api import song
from ebnr.core.types import (
    Album,
    AudioData,
    Encoding,
    LyricData,
    Playlist,
    Quality,
    SongInfo,
)

audio_cache = TTLCache(maxsize=1024, ttl=get_config().audio_cache_timeout)
song_info_cache = LFUCache(maxsize=1024)
lyric_cache = LFUCache(maxsize=1024)
playlist_cache = LFUCache(maxsize=1024)
album_cache = LFUCache(maxsize=1024)


def cache_get(cache: Cache, *key: Any):
    if not get_config().api_cache:
        return None
    if key in cache:
        return cache[key]
    return None


def cache_set[T](cache: Cache, value: T, *key: Any) -> T:
    if not get_config().api_cache:
        return value
    if value is None:
        return value
    cache[key] = value
    return value


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.FLAC,
) -> list[AudioData | None]:
    if get_config().audio_cache_timeout == 0:
        return await song.get_audio(ids, quality, encoding)
    if data := cache_get(audio_cache, tuple(ids), quality, encoding):
        return data
    return cache_set(
        audio_cache,
        await song.get_audio(ids, quality, encoding),
        tuple(ids),
        quality,
        encoding,
    )


async def get_song_info(ids: list[int]) -> list[SongInfo | None]:
    if data := cache_get(song_info_cache, *ids):
        return data
    return cache_set(
        song_info_cache,
        await song.get_song_info(ids),
        *ids,
    )


async def get_lyric(id: int) -> LyricData:
    if data := cache_get(lyric_cache, id):
        return data
    return cache_set(
        lyric_cache,
        await song.get_lyric(id),
        id,
    )


async def get_playlist(id: int) -> Optional[Playlist]:
    if data := cache_get(playlist_cache, id):
        return data
    return cache_set(
        playlist_cache,
        await song.get_playlist(id),
        id,
    )


async def get_album(id: int) -> Optional[Album]:
    if data := cache_get(album_cache, id):
        return data
    return cache_set(
        album_cache,
        await song.get_album(id),
        id,
    )
