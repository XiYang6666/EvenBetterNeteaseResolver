import itertools

import pytest

from ebnr.core.client import EBNR
from tests.core.constants import (
    ALBUM_LIST,
    ID_LIST,
    IDS_LIST,
    KEYWORD_LIST,
    PLAYLIST_LIST,
)


@pytest.fixture
def client():
    client = EBNR()
    return client


@pytest.mark.parametrize("ids", itertools.chain(IDS_LIST, map(lambda x: [x], ID_LIST)))
@pytest.mark.asyncio
async def test_audio(client: EBNR, ids: list[int]):
    await client.song.get_audio(ids)


@pytest.mark.parametrize("ids", itertools.chain(IDS_LIST, map(lambda x: [x], ID_LIST)))
@pytest.mark.asyncio
async def test_song_info(client: EBNR, ids: list[int]):
    await client.song.get_song_info(ids)


@pytest.mark.parametrize("id", ID_LIST)
@pytest.mark.asyncio
async def test_lyric(client: EBNR, id: int):
    await client.song.get_lyric(id)


@pytest.mark.parametrize("keyword", KEYWORD_LIST)
@pytest.mark.asyncio
async def test_search(client: EBNR, keyword: str):
    await client.song.search(keyword, limit=10)


@pytest.mark.parametrize("id", PLAYLIST_LIST)
@pytest.mark.asyncio
async def test_playlist(client: EBNR, id: int):
    await client.song.get_playlist(id)


@pytest.mark.parametrize("id", PLAYLIST_LIST)
@pytest.mark.asyncio
async def test_tracks(client: EBNR, id: int):
    await client.song.get_tracks(id)


@pytest.mark.parametrize("id", ALBUM_LIST)
@pytest.mark.asyncio
async def test_album(client: EBNR, id: int):
    await client.song.get_album(id)
