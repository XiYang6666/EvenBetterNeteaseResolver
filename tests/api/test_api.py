from tests.api.client import client

VALID_ALBUM_ID = 38591089
VALID_SONG_ID = 557581314
VALID_SONG_ID_LIST = [557581314, 1357960252]
VALID_PLAY_LIST_ID = 625445570


def test_album():
    response = client.get(f"/album/https://music.163.com/album?id={VALID_ALBUM_ID}")
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


def test_audio():
    response = client.get(f"/audio/https://music.163.com/song?id={VALID_SONG_ID}")
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


def test_info():
    response = client.get(f"/info/https://music.163.com/song?id={VALID_SONG_ID}")
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


def test_meting():
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
        "/meting/", params={"type": "playlist", "id": f"{VALID_PLAY_LIST_ID}"}
    )
    response.raise_for_status()
    response.json()


def test_playlist():
    response = client.get(
        f"/playlist/https://music.163.com/playlist?id={VALID_PLAY_LIST_ID}"
    )
    response.raise_for_status()
    response.json()

    response = client.get("/playlist", params={"id": f"{VALID_PLAY_LIST_ID}"})
    response.raise_for_status()
    response.json()

    response = client.get(
        "/playlist",
        params={"link": f"https://music.163.com/playlist?id={VALID_PLAY_LIST_ID}"},
    )
    response.raise_for_status()
    response.json()


def test_resolve():
    response = client.get(
        f"/resolve/https://music.163.com/song?id={VALID_SONG_ID}",
        follow_redirects=False,
    )
    if response.status_code != 307:
        response.raise_for_status()
        assert response.status_code == 307
