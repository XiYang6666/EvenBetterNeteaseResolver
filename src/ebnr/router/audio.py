import urllib.parse
from dataclasses import dataclass
from typing import Optional, cast

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import RedirectResponse

from ebnr.core.types import AudioInfo, Quality
from ebnr.services.cached_api.song import get_audio
from ebnr.utils import NeteaseLinkInfo, parse_netease_link

router = APIRouter(prefix="/audio", tags=["音频信息"])


@router.get("/{link:path}", response_model=AudioInfo)
@router.head("/{link:path}", include_in_schema=False)
async def audio_link(link: str, id: Optional[int] = None):
    """
    根据网易云音乐链接获取音频信息, 无法获取时返回错误码 404.
    """
    if link == "":
        return RedirectResponse(f"/audio?{urllib.parse.urlencode({'id': id})}")
    link_info = parse_netease_link(link, id)
    if link_info is None or link_info.type != "song":
        raise HTTPException(400, "Invalid Link")
    data = await get_audio([link_info.id])
    if not (data and data[0]):
        raise HTTPException(404, "Song Not Found")
    return data[0]


@router.get("")
@router.head("", include_in_schema=False)
async def audio_query(
    id: Optional[list[int]] = Query(None),
    link: Optional[list[str]] = Query(None),
    quality: Quality = Quality.STANDARD,
) -> AudioInfo | list[AudioInfo | None]:
    """
    ## 获取音频信息

    id, link 应至少传入一种, 同时传入时优先级 id > link.\n
    如果传入单个 id 或 link 则返回 `AudioData`, 无法获取时返回错误码 404.\n
    如果传入多个 id 或 link 则返回 `(AudioData | null)[]`, 列表对应传入的 id 顺序, 无法获取的歌曲将用 `null` 占位.
    """
    if not id and not link:
        raise ValueError("At least one of id or link must be provided")
    if id and len(id) == 1:
        data = await get_audio([int(i) for i in id], quality=quality)
        if not (data and data[0]):
            raise HTTPException(404, "Song Not Found")
        return data[0]
    elif id:
        return await get_audio(id, quality=quality)
    elif link:
        assert link
        link_info_list = list(map(parse_netease_link, link))
        if any(map(lambda x: x is None or x.type != "song", link_info_list)):
            raise HTTPException(400, "Invalid Link")
        ids = [cast(NeteaseLinkInfo, i).id for i in link_info_list]
        data = await get_audio(ids)
        if not data or not data[0]:
            raise HTTPException(404, "Song Not Found")
        return data[0]
    assert False


@dataclass
class PostAudio:
    id: Optional[int] = None
    ids: Optional[list[int]] = None
    link: Optional[str] = None
    links: Optional[list[str]] = None
    quality: Quality = Quality.STANDARD

    def __post_init__(self):
        if not any([self.id, self.ids, self.link, self.links]):
            raise ValueError("At least one of id, ids, link or links must be provided")


@router.post("")
async def audio_post(body: PostAudio = Body(...)) -> AudioInfo | list[AudioInfo | None]:
    """
    ## 获取音频信息

    id, ids, link, links 应至少传入一个, 传入多个时优先级 ids > id > links > link.\n
    如果传入 id 或 link 则返回 `AudioData`, 无法获取时返回错误码 404.\n
    如果传入 ids 或 links 则返回 `(AudioData | null)[]`, 列表对应传入的 ids 或 links 顺序, 无法获取的歌曲将用 `null` 占位.
    """
    if body.ids:
        return await get_audio(body.ids, quality=body.quality)
    elif body.id:
        data = await get_audio([body.id], quality=body.quality)
        if not (data and data[0]):
            raise HTTPException(404, "Song Not Found")
        return data[0]
    elif body.links:
        assert body.links
        link_info_list = list(map(parse_netease_link, body.links))
        if any(map(lambda x: x is None or x.type != "song", link_info_list)):
            raise HTTPException(400, "Invalid Link")
        ids = [cast(NeteaseLinkInfo, i).id for i in link_info_list]
        data = await get_audio(ids, quality=body.quality)
        return data
    elif body.link:
        link_info = parse_netease_link(cast(str, body.link))
        if link_info is None or link_info.type != "song":
            raise HTTPException(400, "Invalid Link")
        data = await get_audio([link_info.id], quality=body.quality)
        if not (data and data[0]):
            raise HTTPException(404, "Song Not Found")
        return data[0]
    assert False
