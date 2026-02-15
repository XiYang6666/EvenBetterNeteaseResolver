from dataclasses import dataclass
from typing import Optional, cast

from fastapi import APIRouter, Body, HTTPException

from ebnr.core.types import SongInfo
from ebnr.services.cached_api.song import search

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("")
@router.head("", include_in_schema=False)
async def search_get(keyword: Optional[str] = None, limit: int = 10) -> list[SongInfo]:
    """
    ## 搜索歌曲

    keyword 必须传入, limit 为可选项.
    返回 `SongInfo[]`.
    """
    if not keyword:
        raise HTTPException(400, "Invalid Request")
    return await search(keyword, limit)


@dataclass
class PostSearch:
    keyword: str
    limit: int = 10


@router.post("")
async def search_post(body: PostSearch = Body(...)) -> list[SongInfo]:
    """
    ## 搜索歌曲

    keyword 必须传入, limit 为可选项.
    返回 `SongInfo[]`.
    """

    return await search(body.keyword, body.limit)
