from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from ebnr.services.cached_api.song import get_audio

router = APIRouter(prefix="/resolve", tags=["音频解析"])


@router.api_route(
    "/{link:path}",
    methods=["GET", "HEAD"],
    response_class=RedirectResponse,
)
async def resolve_link(link: str, id: int):
    """
    根据网易云音乐链接解析歌曲音频, 成功时重定向到音频链接, 无法获取时返回错误码 404.
    """
    if link != "https://music.163.com/song":
        raise HTTPException(400, "Invalid Link")
    data = await get_audio([id])
    if not data:
        raise HTTPException(404, "Song Not Found")
    if not data[0]:
        raise HTTPException(404, "Could Not Get Audio")
    if not data[0].url and data[0].fee != 0:
        raise HTTPException(404, "VIP Song")
    if not data[0].url:
        raise HTTPException(404, "Audio Not Available")
    return RedirectResponse(data[0].url)
