import json
from typing import Optional

from ebnr.core.cryto.eapi import make_eapi_form, make_eapi_header
from ebnr.core.cryto.weapi import make_weapi_form
from ebnr.core.excaptions import NeteaseApiException
from ebnr.core.types import Encoding, Quality
from ebnr.core.utils import make_client


async def get_audio(
    ids: list[int],
    quality: Quality = Quality.STANDARD,
    encoding: Encoding = Encoding.FLAC,
) -> dict:
    request_url = "https://interface3.music.163.com/eapi/song/enhance/player/url/v1"
    eapi_path = "/api/song/enhance/player/url/v1"
    payload = {
        "ids": ids,
        "level": quality.value,
        "encodeType": encoding.value,
        "header": make_eapi_header(),
    }
    if quality == Quality.SKY:
        payload["immerseType"] = "c51"
    form = make_eapi_form(eapi_path, json.dumps(payload))
    async with make_client() as client:
        response = await client.post(request_url, data=form)
    result = response.json()
    if result["code"] != 200:
        raise NeteaseApiException(
            "Failed to get audio info",
            result["code"],
            result.get("message"),
        )
    return result


async def get_song_info(ids: list[int]) -> dict:
    request_url = "https://music.163.com/weapi/v3/song/detail"
    form = make_weapi_form(
        json.dumps(
            {"c": json.dumps([{"id": id} for id in ids]), "ids": json.dumps(ids)}
        )
    )
    async with make_client() as client:
        response = await client.post(request_url, data=form)
    result = response.json()
    if result["code"] != 200:
        raise NeteaseApiException(
            "Failed to get song info",
            result["code"],
            result.get("message"),
        )
    return result


async def get_lyric(id: int) -> dict:
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
        raise NeteaseApiException(
            "Failed to get lyric",
            result["code"],
            result.get("message"),
        )
    return result


async def search(keyword: str, limit: int = 10) -> dict:
    request_url = "https://music.163.com/api/cloudsearch/pc"
    async with make_client() as client:
        response = await client.post(
            request_url,
            data={"s": keyword, "type": 1, "limit": limit},
        )
    result = response.json()
    if result["code"] != 200:
        raise NeteaseApiException(
            "Failed to get audio data",
            result["code"],
            result.get("message"),
        )
    return result


async def get_playlist(id: int) -> Optional[dict]:
    request_url = "https://music.163.com/api/v6/playlist/detail"
    async with make_client() as client:
        response = await client.post(
            request_url,
            data={
                "id": id,
                "n": 1000,
            },
        )
    # request_url = "https://music.163.com/api/linux/forward"
    # req_data = make_linuxapi_data(
    #     "POST",
    #     "https://music.163.com/api/v3/playlist/detail",
    #     {"id": id, "n": 10000, "s": "8"},
    # )
    # form = make_linuxapi_form(json.dumps(req_data))
    # async with make_client(device_type="linux") as client:
    #     response = await client.post(request_url, data=form)
    result = response.json()
    if result["code"] == 404:
        return None
    if result["code"] != 200:
        raise NeteaseApiException(
            "Failed to get playlist data",
            result["code"],
            result.get("message"),
        )
    return result


async def get_album(id: int) -> Optional[dict]:
    request_url = f"https://music.163.com/api/v1/album/{id}"
    async with make_client() as client:
        response = await client.get(request_url)
    result = response.json()
    if result["code"] == 404:
        return None
    if result["code"] != 200:
        raise NeteaseApiException(
            "Failed to get album data",
            result["code"],
            result.get("message"),
        )
    return result
