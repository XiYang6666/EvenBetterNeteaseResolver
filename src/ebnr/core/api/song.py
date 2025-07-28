from ebnr.core.api import raw
from ebnr.core.parser import (
    parse_album_json,
    parse_audio_json,
    parse_lyric_json,
    parse_playlist_json,
    parse_song_json,
)
from ebnr.core.types import Encoding, Quality


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.FLAC,
):
    audios_data = await raw.song.get_audio(ids, quality, encoding)
    if audios_data is None:
        return None
    return [parse_audio_json(audio_data) for audio_data in audios_data["data"]]


async def get_song_info(ids: list[int]):
    songs_info_data = await raw.song.get_song_info(ids)
    if songs_info_data is None:
        return None
    return [parse_song_json(info) for info in songs_info_data["songs"]]


async def get_lyric(id: int):
    lyric_data = await raw.song.get_lyric(id)
    if lyric_data is None:
        return None
    return parse_lyric_json(lyric_data)


async def search(keyword: str, limit: int = 10):
    search_data = await raw.song.search(keyword, limit)
    if search_data is None:
        return None
    return [parse_song_json(song_data) for song_data in search_data["result"]["songs"]]


async def get_playlist(id: int):
    playlist_data = await raw.song.get_playlist(id)
    if playlist_data is None:
        return None
    return parse_playlist_json(playlist_data["playlist"])


async def get_album(id: int):
    album_data = await raw.song.get_album(id)
    if album_data is None:
        return None
    return parse_album_json(album_data)
