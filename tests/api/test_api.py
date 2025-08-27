import pytest
from fastapi.testclient import TestClient

from ebnr import app

VALID_ALBUM_ID = 38591089
VALID_SONG_ID = 557581314
VALID_SONG_ID_LIST = [557581314, 1357960252]
VALID_PLAYLIST_ID = 625445570


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def make_links(base: str, type: str, id: int):
    return [
        # default
        f"/{base}/https://music.163.com/{type}?id={id}",
        f"/{base}/http://music.163.com/{type}?id={id}",
        f"/{base}/music.163.com/{type}?id={id}",
        # y.
        f"/{base}/https://y.music.163.com/{type}?id={id}",
        f"/{base}/http://y.music.163.com/{type}?id={id}",
        f"/{base}/y.music.163.com/{type}?id={id}",
        # /m
        f"/{base}/https://music.163.com/{type}?id={id}",
        f"/{base}/http://music.163.com/{type}?id={id}",
        f"/{base}/music.163.com/{type}?id={id}",
        # path param
        f"/{base}/https://music.163.com/{type}/{id}",
        f"/{base}/http://music.163.com/{type}/{id}",
        f"/{base}/music.163.com/{type}/{id}",
        # y. and /m
        f"/{base}/https://y.music.163.com/m/{type}?id={id}",
        f"/{base}/http://y.music.163.com/m/{type}?id={id}",
        f"/{base}/y.music.163.com/m/{type}?id={id}",
        # y. and path param
        f"/{base}/https://y.music.163.com/{type}/{id}",
        f"/{base}/http://y.music.163.com/{type}/{id}",
        f"/{base}/y.music.163.com/{type}/{id}",
        # /m and path param
        f"/{base}/https://music.163.com/m/{type}/{id}",
        f"/{base}/http://music.163.com/m/{type}/{id}",
        f"/{base}/music.163.com/m/{type}/{id}",
        # y. and /m and path param
        f"/{base}/https://y.music.163.com/m/{type}/{id}",
        f"/{base}/http://y.music.163.com/m/{type}/{id}",
        f"/{base}/y.music.163.com/m/{type}/{id}",
    ]


def test_album(client: TestClient):
    for link in make_links("album", "album", VALID_ALBUM_ID):
        response = client.get(link)
        response.raise_for_status()
        response.json()

    response = client.get("/album", params={"id": f"{VALID_ALBUM_ID}"})
    response.raise_for_status()
    response.json()

    response = client.get(
        "/album", params={"link": f"https://music.163.com/album?id={VALID_ALBUM_ID}"}
    )
    response.raise_for_status()
    response.json()


def test_audio(client: TestClient):
    for link in make_links("audio", "song", VALID_SONG_ID):
        response = client.get(link)
        response.raise_for_status()
        response.json()

    response = client.get("/audio", params={"id": f"{VALID_SONG_ID}"})
    response.raise_for_status()
    response.json()

    response = client.get(
        "/audio", params={"ids": ",".join(map(str, VALID_SONG_ID_LIST))}
    )
    response.raise_for_status()
    response.json()

    response = client.get(
        "/audio", params={"link": f"https://music.163.com/song?id={VALID_SONG_ID}"}
    )
    response.raise_for_status()
    response.json()


def test_info(client: TestClient):
    for link in make_links("info", "song", VALID_SONG_ID):
        response = client.get(link)
        response.raise_for_status()
        response.json()

    response = client.get("/info", params={"id": f"{VALID_SONG_ID}"})
    response.raise_for_status()
    response.json()

    response = client.get(
        "/info", params={"ids": ",".join(map(str, VALID_SONG_ID_LIST))}
    )
    response.raise_for_status()
    response.json()

    response = client.get(
        "/info", params={"link": f"https://music.163.com/song?id={VALID_SONG_ID}"}
    )
    response.raise_for_status()
    response.json()


def test_meting(client: TestClient):
    response = client.get(
        "/meting/",
        params={"type": "url", "id": f"{VALID_SONG_ID}"},
        follow_redirects=False,
    )
    if response.status_code != 307:
        response.raise_for_status()
        assert response.status_code == 307

    response = client.get("/meting/", params={"type": "song", "id": f"{VALID_SONG_ID}"})
    response.raise_for_status()
    response.json()

    response = client.get(
        "/meting/", params={"type": "playlist", "id": f"{VALID_PLAYLIST_ID}"}
    )
    response.raise_for_status()
    response.json()


def test_playlist(client: TestClient):
    for link in make_links("playlist", "playlist", VALID_PLAYLIST_ID):
        response = client.get(link)
        response.raise_for_status()
        response.json()

    response = client.get("/playlist", params={"id": f"{VALID_PLAYLIST_ID}"})
    response.raise_for_status()
    response.json()

    response = client.get(
        "/playlist",
        params={"link": f"https://music.163.com/playlist?id={VALID_PLAYLIST_ID}"},
    )
    response.raise_for_status()
    response.json()


def test_resolve(client: TestClient):
    for link in make_links("resolve", "song", VALID_SONG_ID):
        response = client.get(link, follow_redirects=False)
        if response.status_code != 307:
            response.raise_for_status()
            assert response.status_code == 307
