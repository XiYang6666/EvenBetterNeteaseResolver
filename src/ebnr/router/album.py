import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from ebnr.services.cached_api.song import get_album

router = APIRouter(prefix="/album")


@router.get("/{link:path}")
async def album_link(link: str, id: int):
    if link != "https://music.163.com/album":
        raise HTTPException(400, "Invalid Link")
    data = await get_album(id)
    return data


@router.get("/")
async def album_get(
    id: Optional[int] = None,
    link: Optional[str] = None,
):
    if not id and not link:
        raise HTTPException(400, "Invalid Request")
    elif id:
        result = await get_album(id)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result
    else:
        url = urllib.parse.urlparse(link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_album(id)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result


@dataclass
class PostPlaylistInfo:
    id: Optional[int]
    link: Optional[str]

    def __post_init__(self):
        if not self.id and not self.link:
            raise ValueError("Invalid Request Data")


@router.post("/")
async def album_post(data: PostPlaylistInfo = Body(...)):
    if data.id:
        result = await get_album(data.id)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result
    else:
        url = urllib.parse.urlparse(data.link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_album(id)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result
