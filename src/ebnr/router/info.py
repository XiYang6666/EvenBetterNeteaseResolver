import urllib.parse
from dataclasses import dataclass
from typing import Optional, cast

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import RedirectResponse

from ebnr.core.types import SongInfo
from ebnr.services.cached_api.song import get_song_info
from ebnr.utils import NeteaseLinkInfo, parse_netease_link

router = APIRouter(prefix="/info", tags=["歌曲信息"])


@router.get("/{link:path}", response_model=SongInfo)
@router.head("/{link:path}", include_in_schema=False)
async def info_link(link: str, id: Optional[int] = None):
    """
    根据网易云音乐链接获取歌曲信息, 无法获取时返回错误码 404.
    """
    if link == "":
        return RedirectResponse(f"/info?{urllib.parse.urlencode({'id': id})}")
    link_info = parse_netease_link(link, id)
    if link_info is None or link_info.type != "song":
        raise HTTPException(400, "Invalid Link")
    data = await get_song_info([link_info.id])
    if not (data and data[0]):
        raise HTTPException(404, "Song Not Found")
    return data[0]


@router.get("")
@router.head("", include_in_schema=False)
async def info_get(
    id: Optional[list[int]] = Query(None),
    link: Optional[list[str]] = Query(None),
) -> SongInfo | list[SongInfo | None]:
    """
    ## 获取音频信息

    id, ids, link 应至少传入一种, 传入多个时优先级 id > link.\n
    如果传入单个 id 或 link 则返回 `AudioData`, 无法获取时返回错误码 404.\n
    如果传入多个 id 或 link 则返回 `(AudioData | null)[]`, 列表对应传入的 ids 顺序, 无法获取的歌曲将用 `null` 占位.
    """
    if not id and not link:
        raise ValueError("At least one of id or link must be provided")
    if id and len(id) == 1:
        data = await get_song_info(id)
        if not (data and data[0]):
            raise HTTPException(404, "Song Not Found")
        return data[0]
    elif id:
        return await get_song_info(id)
    elif link:
        assert link
        link_info_list = list(map(parse_netease_link, link))
        if any(map(lambda x: x is None or x.type != "song", link_info_list)):
            raise HTTPException(400, "Invalid Link")
        ids = [cast(NeteaseLinkInfo, i).id for i in link_info_list]
        data = await get_song_info(ids)
        if not data or not data[0]:
            raise HTTPException(404, "Song Not Found")
        return data[0]
    assert False


@dataclass
class PostInfo:
    id: Optional[int] = None
    ids: Optional[list[int]] = None
    link: Optional[str] = None
    links: Optional[list[str]] = None

    def __post_init__(self):
        if not any([self.id, self.ids, self.link, self.links]):
            raise ValueError("At least one of id, ids, link or links must be provided")


@router.post("")
async def info_post(body: PostInfo = Body(...)) -> SongInfo | list[SongInfo | None]:
    """
    ## 获取音频信息

    id, ids, link, links 应至少传入一个, 传入多个时优先级 ids > id > links > link.\n
    如果传入 id 或 link 则返回 `AudioData`, 无法获取时返回错误码 404.\n
    如果传入 ids 或 links 则返回 `(AudioData | null)[]`, 列表对应传入的 ids 或 links 顺序, 无法获取的歌曲将用 `null` 占位.
    """
    if body.ids:
        return await get_song_info([int(i) for i in body.ids])
    elif body.id:
        data = await get_song_info([body.id])
        if not (data and data[0]):
            raise HTTPException(404, "Song Not Found")
        return data[0]
    elif body.links:
        assert body.links
        link_info_list = list(map(parse_netease_link, body.links))
        if any(map(lambda x: x is None or x.type != "song", link_info_list)):
            raise HTTPException(400, "Invalid Link")
        ids = [cast(NeteaseLinkInfo, i).id for i in link_info_list]
        data = await get_song_info(ids)
        return data
    elif body.link:
        link_info = parse_netease_link(cast(str, body.link))
        if link_info is None or link_info.type != "song":
            raise HTTPException(400, "Invalid Link")
        data = await get_song_info([link_info.id])
        if not data or not data[0]:
            raise HTTPException(404, "Song Not Found")
        return data[0]
    assert False
