from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from ebnr.services.cached_api.song import get_audio
from ebnr.utils import parse_netease_link

router = APIRouter(prefix="/resolve", tags=["音频解析"])


@router.get("/{link:path}", response_class=RedirectResponse)
@router.head("/{link:path}", include_in_schema=False)
async def resolve_link(link: str, id: Optional[int] = None):
    """
    根据网易云音乐链接解析歌曲音频, 成功时重定向到音频链接, 无法获取时返回错误码 404.
    """
    link_info = parse_netease_link(link, id)
    if link_info is None or link_info.type != "song":
        raise HTTPException(400, "Invalid Link")
    data = await get_audio([link_info.id])
    if not (data and data[0]):
        raise HTTPException(404, "Song Not Found")
    if not data[0].url and data[0].fee and not data[0].payed:
        raise HTTPException(404, "VIP Song")
    if not data[0].url:
        raise HTTPException(404, "Audio Not Available")
    return RedirectResponse(data[0].url)
