import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from ebnr.core.types import SongInfo
from ebnr.services.cached_api.song import get_song_info

router = APIRouter(prefix="/info")


@router.api_route("/{link:path}", methods=["GET", "HEAD"])
async def info_link(link: str, id: int) -> SongInfo:
    if link != "https://music.163.com/song":
        raise HTTPException(400, "Invalid Link")
    data = await get_song_info([id])
    if not data or not data[0]:
        raise HTTPException(404, "Song Not Found")
    return data[0]


@router.api_route("/", methods=["GET", "HEAD"])
async def info_get(
    id: Optional[int] = None,
    ids: Optional[str] = None,
    link: Optional[str] = None,
) -> SongInfo | list[SongInfo | None]:
    if not id and not ids and not link:
        raise HTTPException(400, "Invalid Request")
    if ids:
        result = await get_song_info([int(i) for i in ids.split(",")])
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result
    elif id:
        result = await get_song_info([id])
        if not result or not result[0]:
            raise HTTPException(404, "Song Not Found")
        return result[0]
    else:
        url = urllib.parse.urlparse(link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_song_info([id])
        if not result or not result[0]:
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
async def info_post(data: PostSongInfo = Body(...)) -> SongInfo | list[SongInfo | None]:
    if data.ids:
        result = await get_song_info([int(i) for i in data.ids])
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result
    elif data.id:
        result = await get_song_info([data.id])
        if not result or not result[0]:
            raise HTTPException(404, "Song Not Found")
        return result[0]
    else:
        url = urllib.parse.urlparse(data.link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_song_info([id])
        if not result or not result[0]:
            raise HTTPException(404, "Song Not Found")
        return result[0]
