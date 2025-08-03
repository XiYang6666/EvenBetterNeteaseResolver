import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from ebnr.core.types import Quality
from ebnr.services.cached_api.song import get_audio

router = APIRouter(prefix="/audio")


@router.api_route("/{link:path}", methods=["GET", "HEAD"])
async def audio_link(link: str, id: int):
    if link != "https://music.163.com/song":
        raise HTTPException(400, "Invalid Link")
    data = await get_audio([id])
    if not data:
        raise HTTPException(404, "Song Not Found")
    return data[0]


@router.api_route("/", methods=["GET", "HEAD"])
async def audio_query(
    id: Optional[int] = None,
    ids: Optional[str] = None,
    link: Optional[str] = None,
    quality: Quality = Quality.STANDARD,
):
    if not ids and not id and not link:
        raise HTTPException(400, "Invalid Request")
    if ids:
        return await get_audio([int(i) for i in ids.split(",")], quality=quality)
    elif id:
        result = await get_audio([id], quality=quality)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result[0]
    else:
        url = urllib.parse.urlparse(link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_audio([id], quality=quality)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result[0]


@dataclass
class PostAudioData:
    ids: Optional[list[int]]
    id: Optional[int]
    link: Optional[str]
    quality: Quality = Quality.STANDARD

    def __post_init__(self):
        if not self.ids and not self.id and not self.link:
            raise ValueError("Invalid Request Data")


@router.post("/")
async def audio_post(data: PostAudioData = Body(...)):
    if data.ids:
        return await get_audio([int(i) for i in data.ids], quality=data.quality)
    elif data.id:
        result = await get_audio([data.id], quality=data.quality)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result[0]
    else:
        url = urllib.parse.urlparse(data.link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_audio([id], quality=data.quality)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result[0]
