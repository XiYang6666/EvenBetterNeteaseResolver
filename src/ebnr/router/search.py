from dataclasses import dataclass
from fastapi import APIRouter, Body, HTTPException

from ebnr.core.types import SongInfo
from ebnr.services.cached_api.song import search

router = APIRouter(prefix="/search", tags=["歌曲搜索"])


@router.get("")
@router.head("", include_in_schema=False)
async def search_get(
    keyword: str = "",
    limit: int = 10
) -> list[SongInfo]:
    """
    ## 搜索歌曲

    keyword 必须传入, limit 为可选项.
    成功时返回 `SongInfo[]`, 无法获取歌单时返回错误码 404.
    """
    if not keyword:
        raise HTTPException(400, "Invalid Request")
    return await search(keyword, limit)

@dataclass
class PostSearch:
    keyword: str = ""
    limit: int = 10

    def __post_init__(self):
        if  not self.keyword:
            raise ValueError("Invalid Request Data")


@router.post("")
async def search_post(body: PostSearch = Body(...)) -> list[SongInfo]:
    return await search(body.keyword, body.limit)