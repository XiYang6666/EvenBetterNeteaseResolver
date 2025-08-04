import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from ebnr.core.types import Album
from ebnr.services.cached_api.song import get_album

router = APIRouter(prefix="/album", tags=["专辑"])


@router.api_route("/{link:path}", methods=["GET", "HEAD"])
async def album_link(link: str, id: int) -> Album:
    if link != "https://music.163.com/album":
        raise HTTPException(400, "Invalid Link")
    data = await get_album(id)
    if not data:
        raise HTTPException(404, "Album Not Found")
    return data


@router.api_route("/", methods=["GET", "HEAD"])
async def album_get(
    id: Optional[int] = None,
    link: Optional[str] = None,
) -> Album:
    if not id and not link:
        raise HTTPException(400, "Invalid Request")
    elif id:
        result = await get_album(id)
        if not result:
            raise HTTPException(404, "Album Not Found")
        return result
    else:
        url = urllib.parse.urlparse(link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_album(id)
        if not result:
            raise HTTPException(404, "Album Not Found")
        return result


@dataclass
class PostPlaylistInfo:
    id: Optional[int]
    link: Optional[str]

    def __post_init__(self):
        if not self.id and not self.link:
            raise ValueError("Invalid Request Data")


@router.post("/")
async def album_post(data: PostPlaylistInfo = Body(...)) -> Album:
    if data.id:
        result = await get_album(data.id)
        if not result:
            raise HTTPException(404, "Album Not Found")
        return result
    else:
        url = urllib.parse.urlparse(data.link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_album(id)
        if not result:
            raise HTTPException(404, "Album Not Found")
        return result
