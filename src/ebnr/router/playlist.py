import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse

from ebnr.core.types import Playlist
from ebnr.services.cached_api.song import get_playlist

router = APIRouter(prefix="/playlist", tags=["歌单"])


@router.api_route("/{link:path}", methods=["GET", "HEAD"], response_model=Playlist)
async def playlist_link(link: str, id: int):
    """
    根据网易云音乐链接获取歌单信息, 无法获取时返回错误码 404.
    """
    if link == "":
        return RedirectResponse(f"/playlist?{urllib.parse.urlencode({'id': id})}")
    if link != "https://music.163.com/playlist":
        raise HTTPException(400, "Invalid Link")
    data = await get_playlist(id)
    if not data:
        raise HTTPException(404, "Playlist Not Found")
    return data


@router.api_route("", methods=["GET", "HEAD"])
async def playlist_get(
    id: Optional[int] = None,
    link: Optional[str] = None,
) -> Playlist:
    """
    ## 获取歌单信息

    id, link 应至少传入一个, 传入多个时优先级 id > link.\n
    成功时返回 `Playlist`, 无法获取时返回错误码 404.
    """
    if not id and not link:
        raise HTTPException(400, "Invalid Request")
    elif id:
        result = await get_playlist(id)
        if not result:
            raise HTTPException(404, "Playlist Not Found")
        return result
    else:
        url = urllib.parse.urlparse(link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_playlist(id)
        if not result:
            raise HTTPException(404, "PLaylist Not Found")
        return result


@dataclass
class PostPlaylistInfo:
    id: Optional[int]
    link: Optional[str]

    def __post_init__(self):
        if not self.id and not self.link:
            raise ValueError("Invalid Request Data")


@router.post("")
async def playlist_post(data: PostPlaylistInfo = Body(...)) -> Playlist:
    """
    ## 获取歌单信息

    id, link 应至少传入一个, 传入多个时优先级 id > link.\n
    成功时返回 `Playlist`, 无法获取时返回错误码 404.
    """
    if data.id:
        result = await get_playlist(data.id)
        if not result:
            raise HTTPException(404, "Playlist Not Found")
        return result
    else:
        url = urllib.parse.urlparse(data.link)
        assert isinstance(url.query, str)
        parser_qs = urllib.parse.parse_qs(url.query)
        id = int(parser_qs["id"][0])
        result = await get_playlist(id)
        if not result:
            raise HTTPException(404, "Playlist Not Found")
        return result
