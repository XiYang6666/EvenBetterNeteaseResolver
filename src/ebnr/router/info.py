import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from ebnr.core.api.song import get_song_info

router = APIRouter(prefix="/info")


@router.get("/{link:path}")
async def info_link(link: str, id: int):
    if link != "https://music.163.com/song":
        raise HTTPException(400, "Invalid Link")
    data = await get_song_info([id])
    if not data:
        raise HTTPException(404, "Song Not Found")
    return data[0]


@router.get("/")
async def info_get(
    id: Optional[int] = None,
    ids: Optional[str] = None,
    link: Optional[str] = None,
):
    if not id and not ids and not link:
        raise HTTPException(400, "Invalid Request")
    if ids:
        result = await get_song_info([int(i) for i in ids.split(",")])
    elif id:
        result = await get_song_info([id])
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result[0]
    else:
        url = urllib.parse.urlparse(link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_song_info([id])
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result[0]


@dataclass
class PostSongInfo:
    ids: Optional[list[int]]
    id: Optional[int]
    link: Optional[str]

    def __post_init__(self):
        if not self.ids and not self.id and not self.link:
            raise ValueError("Invalid Request Data")


@router.post("/")
async def info_post(data: PostSongInfo = Body(...)):
    if data.ids:
        return await get_song_info([int(i) for i in data.ids])
    elif data.id:
        result = await get_song_info([data.id])
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result[0]
    else:
        url = urllib.parse.urlparse(data.link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_song_info([id])
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result[0]
