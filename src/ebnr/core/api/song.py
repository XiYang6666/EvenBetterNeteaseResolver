import asyncio
from itertools import chain
from typing import Optional

from ebnr.core.api import raw
from ebnr.core.parser import (
    parse_album_json,
    parse_audio_json,
    parse_lyric_json,
    parse_playlist_json,
    parse_song_json,
)
from ebnr.core.types import Encoding, Quality, SongInfo
from ebnr.core.utils import extract_playlist_tracks, remap_result


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.FLAC,
    *,
    cookies: Optional[dict[str, str]] = None,
):
    # 2000 一批都没问题, 但大了容易超时
    batches = [ids[i : i + 1000] for i in range(0, len(ids), 1000)]

    async def get_audio_batch(current_ids: list[int]):
        audios_data = await raw.song.get_audio(
            current_ids, quality, encoding, cookies=cookies
        )
        return [parse_audio_json(audio_data) for audio_data in audios_data["data"]]

    tasks = [get_audio_batch(current_ids) for current_ids in batches]

    results = await asyncio.gather(*tasks)
    return remap_result(ids, chain(*results))


async def get_song_info(
    ids: list[int],
    *,
    cookies: Optional[dict[str, str]] = None,
):
    batches = [ids[i : i + 1000] for i in range(0, len(ids), 1000)]

    async def get_song_batch(current_ids: list[int]):
        songs_info_data = await raw.song.get_song_info(current_ids, cookies=cookies)
        return [parse_song_json(info) for info in songs_info_data["songs"]]

    tasks = [get_song_batch(current_ids) for current_ids in batches]

    results = await asyncio.gather(*tasks)
    return remap_result(ids, chain(*results))


async def get_lyric(
    id: int,
    *,
    cookies: Optional[dict[str, str]] = None,
):
    lyric_data = await raw.song.get_lyric(id, cookies=cookies)
    return parse_lyric_json(lyric_data)


async def search(
    keyword: str,
    limit: int = 10,
    *,
    cookies: Optional[dict[str, str]] = None,
):
    search_data = await raw.song.search(keyword, limit, cookies=cookies)
    return [parse_song_json(song_data) for song_data in search_data["result"]["songs"]]


async def get_playlist(
    id: int,
    *,
    cookies: Optional[dict[str, str]] = None,
):
    if (playlist_data := await raw.song.get_playlist(id, cookies=cookies)) is None:
        return None
    return parse_playlist_json(playlist_data["playlist"])


async def get_tracks(
    id: int,
    limit: int = 1000,
    page: int = 0,
    *,
    cookies: Optional[dict[str, str]] = None,
) -> Optional[list[SongInfo | None]]:
    if (data := await get_playlist(id, cookies=cookies)) is None:
        return None
    extracted = extract_playlist_tracks(data.track_ids, data.tracks, limit, page)
    return extracted.known + (await get_song_info(extracted.unknown, cookies=cookies))


async def get_album(
    id: int,
    *,
    cookies: Optional[dict[str, str]] = None,
):
    if (album_data := await raw.song.get_album(id, cookies=cookies)) is None:
        return None
    return parse_album_json(album_data)
