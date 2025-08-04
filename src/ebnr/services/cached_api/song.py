from typing import Optional

from cachetools import LFUCache, TTLCache

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

audio_cache = TTLCache(maxsize=1024, ttl=3600)
song_info_cache = LFUCache(maxsize=1024)
lyric_cache = LFUCache(maxsize=1024)
playlist_cache = LFUCache(maxsize=1024)
album_cache = LFUCache(maxsize=1024)


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.FLAC,
) -> Optional[list[Optional[AudioData]]]:
    if (tuple(ids), quality, encoding) in audio_cache and get_config().api_cache:
        return audio_cache[(tuple(ids), quality, encoding)]
    audio_data = await song.get_audio(ids, quality, encoding)
    if audio_data is not None and get_config().api_cache:
        audio_cache[(tuple(ids), quality, encoding)] = audio_data
    return audio_data


async def get_song_info(ids: list[int]) -> Optional[list[SongInfo]]:
    if tuple(ids) in song_info_cache and get_config().api_cache:
        return song_info_cache[tuple(ids)]
    song_info_data = await song.get_song_info(ids)
    if song_info_data is not None and get_config().api_cache:
        song_info_cache[tuple(ids)] = song_info_data
    return song_info_data


async def get_lyric(id: int) -> Optional[LyricData]:
    if id in lyric_cache and get_config().api_cache:
        return lyric_cache[id]
    lyric_data = await song.get_lyric(id)
    if lyric_data is not None and get_config().api_cache:
        lyric_cache[id] = lyric_data
    return lyric_data


async def get_playlist(id: int) -> Optional[Playlist]:
    if id in playlist_cache and get_config().api_cache:
        return playlist_cache[id]
    playlist_data = await song.get_playlist(id)
    if playlist_data is not None and get_config().api_cache:
        playlist_cache[id] = playlist_data
    return playlist_data


async def get_album(id: int) -> Optional[Album]:
    if id in album_cache and get_config().api_cache:
        return album_cache[id]
    album_data = await song.get_album(id)
    if album_data is not None and get_config().api_cache:
        album_cache[id] = album_data
    return album_data
