import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse

from ebnr.core.types import Album
from ebnr.services.cached_api.song import get_album
from ebnr.utils import parse_netease_link

router = APIRouter(prefix="/album", tags=["专辑"])


@router.get("/{link:path}", response_model=Album)
@router.head("/{link:path}", include_in_schema=False)
async def album_link(link: str, id: Optional[int] = None):
    """
    根据网易云音乐链接获取专辑信息, 无法获取时返回错误码 404.
    """
    if link == "":
        return RedirectResponse(f"/album?{urllib.parse.urlencode({'id': id})}")
    link_info = parse_netease_link(link, id)
    if link_info is None or link_info.type != "album":
        raise HTTPException(400, "Invalid Link")
    data = await get_album(link_info.id)
    if not data:
        raise HTTPException(404, "Album Not Found")
    return data


@router.get("")
@router.head("", include_in_schema=False)
async def album_get(
    id: Optional[int] = None,
    link: Optional[str] = None,
) -> Album:
    """
    ## 获取专辑信息

    id, link 应至少传入一个, 传入多个时优先级 id > link.\n
    成功时返回 `Album`, 无法获取返回错误码 404.
    """
    if not id and not link:
        raise HTTPException(422, "At least one of id, ids or link must be provided")
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
class PostAlbum:
    id: Optional[int]
    link: Optional[str]

    def __post_init__(self):
        if not self.id and not self.link:
            raise ValueError("At least one of id, ids or link must be provided")


@router.post("")
async def album_post(data: PostAlbum = Body(...)) -> Album:
    """
    ## 获取专辑信息

    id, link 应至少传入一个, 传入多个时优先级 id > link.\n
    成功时返回 `Album`, 无法获取返回错误码 404.
    """
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
