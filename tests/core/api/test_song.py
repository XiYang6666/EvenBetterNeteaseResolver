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
from tests.core.constants import (
    ALBUM_LIST,
    ID_LIST,
    IDS_LIST,
    KEYWORD_LIST,
    PLAYLIST_LIST,
)


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
