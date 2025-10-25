import urllib.parse
from dataclasses import dataclass
from typing import Optional, cast

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse

from ebnr.core.types import SongInfo
from ebnr.services.cached_api.song import get_tracks
from ebnr.utils import parse_netease_link

router = APIRouter(prefix="/tracks", tags=["歌单歌曲"])


@router.get("/{link:path}", response_model=list[SongInfo | None])
@router.head("/{link:path}", include_in_schema=False)
async def tracks_link(link: str, id: Optional[int] = None):
    """
    根据网易云音乐链接获取歌单内所有歌曲信息, 无法获取歌单时返回错误码 404, 无法获取的歌曲用 `null` 占位.
    """
    if link == "":
        return RedirectResponse(f"/tracks?{urllib.parse.urlencode({'id': id})}")
    link_info = parse_netease_link(link, id)
    if link_info is None or link_info.type != "playlist":
        raise HTTPException(400, "Invalid Link")
    data = await get_tracks(link_info.id, 100000)
    if not data:
        raise HTTPException(404, "Playlist Not Found")
    return data


@router.get("")
@router.head("", include_in_schema=False)
async def tracks_get(
    id: Optional[int] = None,
    link: Optional[str] = None,
    limit: int = 100000,
    page: int = 0,
) -> list[SongInfo | None]:
    """
    ## 获取歌单内歌曲信息

    id, link 应至少传入一个, 传入多个时优先级 id > link.\n
    成功时返回 `(SongInfo | null)[]`, 无法获取歌单时返回错误码 404, 无法获取的歌曲用 `null` 占位.
    """
    if not id and not link:
        raise HTTPException(400, "Invalid Request")
    elif id:
        result = await get_tracks(id, limit, page)
        if not result:
            raise HTTPException(404, "Playlist Not Found")
        return result
    else:
        link_info = parse_netease_link(cast(str, link))
        if link_info is None or link_info.type != "playlist":
            raise HTTPException(400, "Invalid Link")
        result = await get_tracks(link_info.id, limit, page)
        if not result:
            raise HTTPException(404, "Playlist Not Found")
        return result


@dataclass
class PostTracks:
    id: Optional[int] = None
    link: Optional[str] = None
    limit: int = 100000
    page: int = 0

    def __post_init__(self):
        if not self.id and not self.link:
            raise ValueError("Invalid Request Data")


@router.post("")
async def tracks_post(body: PostTracks = Body(...)) -> list[SongInfo | None]:
    """
    ## 获取歌单内歌曲信息

    id, link 应至少传入一个, 传入多个时优先级 id > link.\n
    成功时返回 `(SongInfo | null)[]`, 无法获取歌单时返回错误码 404, 无法获取的歌曲用 `null` 占位.
    """
    if body.id:
        data = await get_tracks(body.id, body.limit, body.page)
        if not data:
            raise HTTPException(404, "Playlist Not Found")
        return data
    else:
        link_info = parse_netease_link(cast(str, body.link))
        if link_info is None or link_info.type != "playlist":
            raise HTTPException(400, "Invalid Link")
        data = await get_tracks(link_info.id, body.limit, body.page)
        if not data:
            raise HTTPException(404, "Playlist Not Found")
        return data
