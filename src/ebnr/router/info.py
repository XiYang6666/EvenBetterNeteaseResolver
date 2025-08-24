import urllib.parse
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse

from ebnr.core.types import SongInfo
from ebnr.services.cached_api.song import get_song_info

router = APIRouter(prefix="/info", tags=["歌曲信息"])


@router.get("/{link:path}", response_model=SongInfo)
@router.head("/{link:path}", include_in_schema=False)
async def info_link(link: str, id: int):
    """
    根据网易云音乐链接获取歌曲信息, 无法获取时返回错误码 404.
    """
    if link == "":
        return RedirectResponse(f"/info?{urllib.parse.urlencode({'id': id})}")
    if link != "https://music.163.com/song":
        raise HTTPException(400, "Invalid Link")
    data = await get_song_info([id])
    if not data or not data[0]:
        raise HTTPException(404, "Song Not Found")
    return data[0]


@router.get("")
@router.head("", include_in_schema=False)
async def info_get(
    id: Optional[int] = None,
    ids: Optional[str] = None,
    link: Optional[str] = None,
) -> SongInfo | list[SongInfo | None]:
    """
    ## 获取音频信息

    id, ids, link 应至少传入一个, 传入多个时优先级 ids > id > link.\n
    如果传入 id 或 link 则返回 `AudioData`, 无法获取时返回错误码 404.\n
    如果传入 ids 则返回 `(AudioData | null)[]`, 列表对应传入的 ids 顺序, 无法获取的歌曲将用 `null` 占位.
    """
    if not id and not ids and not link:
        raise ValueError("At least one of id, ids or link must be provided")
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
class PostInfo:
    ids: Optional[list[int]]
    id: Optional[int]
    link: Optional[str]

    def __post_init__(self):
        if not self.ids and not self.id and not self.link:
            raise ValueError("At least one of id, ids or link must be provided")


@router.post("")
async def info_post(data: PostInfo = Body(...)) -> SongInfo | list[SongInfo | None]:
    """
    ## 获取音频信息

    id, ids, link 应至少传入一个, 传入多个时优先级 ids > id > link.\n
    如果传入 id 或 link 则返回 `AudioData`, 无法获取时返回错误码 404.\n
    如果传入 ids 则返回 `(AudioData | null)[]`, 列表对应传入的 ids 顺序, 无法获取的歌曲将用 `null` 占位.
    """
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
