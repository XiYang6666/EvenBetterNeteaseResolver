import json
from typing import Optional

from ebnr.core.types import Encoding, Quality
from ebnr.core.utils import make_client, make_eapi_header, make_eapi_params


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.MP3,
) -> Optional[dict]:
    request_url = "https://interface3.music.163.com/eapi/song/enhance/player/url/v1"
    eapi_path = "/api/song/enhance/player/url/v1"
    payload = {
        "ids": ids,
        "level": quality.value,
        "encodeType": encoding.value,
        "header": make_eapi_header(),
    }
    params = make_eapi_params(eapi_path, json.dumps(payload))
    async with make_client() as client:
        response = await client.post(request_url, data={"params": params})
    result = response.json()
    if result["code"] != 200:
        return None
    return result


async def get_song_info(ids: list[int]) -> Optional[dict]:
    request_url = "https://interface3.music.163.com/api/v3/song/detail"
    async with make_client() as client:
        response = await client.post(
            request_url, data={"c": json.dumps([{"id": id, "v": 0} for id in ids])}
        )
    result = response.json()
    if result["code"] != 200:
        return None
    return result


async def get_lyric(id: int) -> Optional[dict]:
    request_url = "https://interface3.music.163.com/api/song/lyric"
    async with make_client() as client:
        response = await client.post(
            request_url,
            data={
                "id": id,
                "cp": "false",
                "tv": "0",
                "lv": "0",
                "rv": "0",
                "kv": "0",
                "yv": "0",
                "ytv": "0",
                "yrv": "0",
            },
        )
    result = response.json()
    if result["code"] != 200:
        return None
    return result


async def search(keyword: str, limit: int = 10) -> Optional[dict]:
    request_url = "https://music.163.com/api/cloudsearch/pc"
    async with make_client() as client:
        response = await client.post(
            request_url,
            data={
                "s": keyword,
                "type": 1,
                "limit": limit,
            },
        )
    result = response.json()
    if result["code"] != 200:
        return None
    return result


async def get_playlist(id: int) -> Optional[dict]:
    request_url = "https://music.163.com/api/v6/playlist/detail"
    async with make_client() as client:
        response = await client.post(
            request_url,
            data={
                "id": id,
            },
        )
    result = response.json()
    if result["code"] != 200:
        return None
    return result


async def get_album(id: int) -> Optional[dict]:
    request_url = f"https://music.163.com/api/v1/album/{id}"
    async with make_client() as client:
        response = await client.get(request_url)
    result = response.json()
    if result["code"] != 200:
        return None
    return result
