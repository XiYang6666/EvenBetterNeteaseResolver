import itertools

import pytest

from ebnr.core.api.song import (
    get_album,
    get_audio,
    get_lyric,
    get_playlist,
    get_song_info,
    get_tracks,
    search,
)

IDS_LIST = [
    [
        557584330,
        557581314,
        557583335,
        557581315,
        557581316,
        557581317,
        557579321,
        557583336,
        557581318,
    ],
    [
        1357960251,
        1357960253,
        1357953772,
        1357953770,
        1357953766,
        1357953774,
        1357953771,
        1357953769,
        1357960254,
        1357960250,
        1357628744,
        1357960252,
        1357953767,
        1357953768,
    ],
]

ID_LIST = [
    557584330,
    557581314,
    557583335,
]

KEYWORD_LIST = [
    "ヨルシカ",
    "水月陵",
    "老人と海",
    "だから僕は音楽を辞めた",
    "鳥の詩",
    "風の止まり木",
]

PLAYLIST_LIST = [
    625445570,  # https://music.163.com/playlist?id=625445570
    588784625,  # https://music.163.com/playlist?id=588784625
    2342914705,  # https://music.163.com/playlist?id=2342914705
]

ALBUM_LIST = [
    163093570,  # https://music.163.com/album?id=163093570
    93148762,  # https://music.163.com/album?id=93148762
    81207880,  # https://music.163.com/album?id=81207880
]


@pytest.mark.parametrize("ids", itertools.chain(IDS_LIST, map(lambda x: [x], ID_LIST)))
@pytest.mark.asyncio
async def test_audio(ids: list[int]):
    await get_audio(ids)


@pytest.mark.parametrize("ids", itertools.chain(IDS_LIST, map(lambda x: [x], ID_LIST)))
@pytest.mark.asyncio
async def test_song_info(ids: list[int]):
    await get_song_info(ids)


@pytest.mark.parametrize("id", ID_LIST)
@pytest.mark.asyncio
async def test_lyric(id: int):
    await get_lyric(id)


@pytest.mark.parametrize("keyword", KEYWORD_LIST)
@pytest.mark.asyncio
async def test_search(keyword: str):
    await search(keyword, limit=10)


@pytest.mark.parametrize("id", PLAYLIST_LIST)
@pytest.mark.asyncio
async def test_playlist(id: int):
    await get_playlist(id)


@pytest.mark.parametrize("id", PLAYLIST_LIST)
@pytest.mark.asyncio
async def test_tracks(id: int):
    await get_tracks(id)


@pytest.mark.parametrize("id", ALBUM_LIST)
@pytest.mark.asyncio
async def test_album(id: int):
    await get_album(id)
