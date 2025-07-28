import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from ebnr.core.api.song import get_playlist

router = APIRouter(prefix="/playlist")


@router.get("/{link:path}")
async def playlist_link(link: str, id: int):
    if link != "https://music.163.com/playlist":
        raise HTTPException(400, "Invalid Link")
    data = await get_playlist(id)
    return data


@router.get("/")
async def plaulist_get(
    id: Optional[int] = None,
    link: Optional[str] = None,
):
    if not id and not link:
        raise HTTPException(400, "Invalid Request")
    elif id:
        result = await get_playlist(id)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result
    else:
        url = urllib.parse.urlparse(link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_playlist(id)
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
async def playlist_post(data: PostPlaylistInfo = Body(...)):
    if data.id:
        result = await get_playlist(data.id)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result
    else:
        url = urllib.parse.urlparse(data.link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_playlist(id)
        if not result:
            raise HTTPException(404, "Song Not Found")
        return result
