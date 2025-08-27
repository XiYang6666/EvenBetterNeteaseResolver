from asyncio import Semaphore, TaskGroup
from functools import wraps
from typing import Callable, Optional

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient, Limits

from ebnr import app

VALID_ALBUM_ID = 38591089
VALID_SONG_ID = 557581314
VALID_SONG_ID_LIST = [557581314, 1357960252]
VALID_PLAYLIST_ID = 625445570


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        limits=Limits(max_connections=30),
    ) as ac:
        yield ac


def catch_exception_group(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except* Exception as eg:
            for e in eg.exceptions:
                print(f"{e.__class__.__name__}: {e}")
            raise eg

    return wrapper


def make_links(type: str, id: int):
    return [
        # default
        f"https://music.163.com/{type}?id={id}",
        f"http://music.163.com/{type}?id={id}",
        f"music.163.com/{type}?id={id}",
        # y.
        f"https://y.music.163.com/{type}?id={id}",
        f"http://y.music.163.com/{type}?id={id}",
        f"y.music.163.com/{type}?id={id}",
        # /m
        f"https://music.163.com/{type}?id={id}",
        f"http://music.163.com/{type}?id={id}",
        f"music.163.com/{type}?id={id}",
        # path param
        f"https://music.163.com/{type}/{id}",
        f"http://music.163.com/{type}/{id}",
        f"music.163.com/{type}/{id}",
        # y. and /m
        f"https://y.music.163.com/m/{type}?id={id}",
        f"http://y.music.163.com/m/{type}?id={id}",
        f"y.music.163.com/m/{type}?id={id}",
        # y. and path param
        f"https://y.music.163.com/{type}/{id}",
        f"http://y.music.163.com/{type}/{id}",
        f"y.music.163.com/{type}/{id}",
        # /m and path param
        f"https://music.163.com/m/{type}/{id}",
        f"http://music.163.com/m/{type}/{id}",
        f"music.163.com/m/{type}/{id}",
        # y. and /m and path param
        f"https://y.music.163.com/m/{type}/{id}",
        f"http://y.music.163.com/m/{type}/{id}",
        f"y.music.163.com/m/{type}/{id}",
    ]


async def get(
    client: AsyncClient,
    link: str,
    params: Optional[dict] = None,
    sem: Optional[Semaphore] = None,
):
    if sem:
        async with sem:
            response = await client.get(link, params=params)
    else:
        response = await client.get(link, params=params)
    response.raise_for_status()
    response.json()


async def post(
    client: AsyncClient,
    link: str,
    json: Optional[dict] = None,
    sem: Optional[Semaphore] = None,
):
    if sem:
        async with sem:
            response = await client.post(link, json=json)
    else:
        response = await client.post(link, json=json)
    response.raise_for_status()
    response.json()


@pytest.mark.asyncio
@catch_exception_group
async def test_album(client: AsyncClient):
    async with TaskGroup() as tg:
        for link in make_links("album", VALID_ALBUM_ID):
            # 拼接链接
            tg.create_task(get(client, f"/album/{link}"))
            # get link
            tg.create_task(get(client, "/album", params={"link": link}))
            # post link
            tg.create_task(post(client, "/album", json={"link": link}))

        # get id
        tg.create_task(get(client, "/album", params={"id": f"{VALID_ALBUM_ID}"}))
        # post id
        tg.create_task(post(client, "/album", json={"id": f"{VALID_ALBUM_ID}"}))


@pytest.mark.asyncio
@catch_exception_group
async def test_audio(client: AsyncClient):
    sem = Semaphore(30)  # 并发太多容易炸
    async with TaskGroup() as tg:
        for link in make_links("song", VALID_SONG_ID):
            # 拼接链接
            tg.create_task(get(client, f"/audio/{link}", sem=sem))

            # get link
            tg.create_task(get(client, "/audio", params={"link": link}, sem=sem))
            # post link
            tg.create_task(post(client, "/audio", json={"link": link}, sem=sem))

        for links in zip(*(make_links("song", id) for id in VALID_SONG_ID_LIST)):
            # get links
            tg.create_task(get(client, "/audio", params={"link": links}, sem=sem))
            # post links
            tg.create_task(post(client, "/audio", json={"links": links}, sem=sem))

        # get id
        tg.create_task(
            get(client, "/audio", params={"id": f"{VALID_SONG_ID}"}, sem=sem)
        )
        # post id
        tg.create_task(post(client, "/audio", json={"id": VALID_SONG_ID}, sem=sem))
        # get ids
        tg.create_task(
            get(client, "/audio", params={"id": VALID_SONG_ID_LIST}, sem=sem)
        )
        # post ids
        tg.create_task(
            post(client, "/audio", json={"ids": VALID_SONG_ID_LIST}, sem=sem)
        )


@pytest.mark.asyncio
@catch_exception_group
async def test_info(client: AsyncClient):
    sem = Semaphore(30)  # 并发太多容易炸
    async with TaskGroup() as tg:
        for link in make_links("song", VALID_SONG_ID):
            # 拼接链接
            tg.create_task(get(client, f"/info/{link}", sem=sem))
            # get link
            tg.create_task(get(client, "/info", params={"link": link}, sem=sem))
            # post link
            tg.create_task(post(client, "/info", json={"link": link}, sem=sem))

        for links in zip(*(make_links("song", id) for id in VALID_SONG_ID_LIST)):
            # get links
            tg.create_task(get(client, "/info", params={"link": links}, sem=sem))
            # post links
            tg.create_task(post(client, "/info", json={"links": links}, sem=sem))

        # get id
        tg.create_task(get(client, "/info", params={"id": f"{VALID_SONG_ID}"}, sem=sem))
        # post id
        tg.create_task(post(client, "/info", json={"id": VALID_SONG_ID}, sem=sem))
        # get ids
        tg.create_task(get(client, "/info", params={"id": VALID_SONG_ID_LIST}, sem=sem))
        # post ids
        tg.create_task(post(client, "/info", json={"ids": VALID_SONG_ID_LIST}, sem=sem))


@pytest.mark.asyncio
async def test_meting(client: AsyncClient):
    response = await client.get(
        "/meting/",
        params={"type": "url", "id": f"{VALID_SONG_ID}"},
        follow_redirects=False,
    )
    if response.status_code != 307:
        response.raise_for_status()
        assert response.status_code == 307

    await get(client, "/meting/", params={"type": "song", "id": f"{VALID_SONG_ID}"})
    await get(
        client, "/meting/", params={"type": "playlist", "id": f"{VALID_PLAYLIST_ID}"}
    )


@pytest.mark.asyncio
@catch_exception_group
async def test_playlist(client: AsyncClient):
    async with TaskGroup() as tg:
        for link in make_links("playlist", VALID_PLAYLIST_ID):
            # 拼接链接
            tg.create_task(get(client, f"/playlist/{link}"))
            # get link
            tg.create_task(get(client, "/playlist", params={"link": link}))
            # post link
            tg.create_task(post(client, "/playlist", json={"link": link}))

        # get id
        tg.create_task(get(client, "/playlist", params={"id": f"{VALID_PLAYLIST_ID}"}))
        # post id
        tg.create_task(post(client, "/playlist", json={"id": f"{VALID_PLAYLIST_ID}"}))


@pytest.mark.asyncio
@catch_exception_group
async def test_resolve(client: AsyncClient):
    for link in make_links("song", VALID_SONG_ID):
        response = await client.get(f"/resolve/{link}", follow_redirects=False)
        if response.status_code != 307:
            response.raise_for_status()
            assert response.status_code == 307
