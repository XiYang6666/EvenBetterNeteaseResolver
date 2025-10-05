from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse, StreamingResponse

from ebnr.config import get_config
from ebnr.services.cached_api.song import get_audio
from ebnr.utils import parse_netease_link, streaming_request

router = APIRouter(prefix="/resolve", tags=["音频解析"])


@router.get("/{link:path}")
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
    if get_config().resolve_type == "redirect":
        return RedirectResponse(data[0].url, get_config().redirect_code)
    elif get_config().resolve_type == "proxy":
        async with httpx.AsyncClient() as client:
            response = await client.get(data[0].url)
        body = response.content
        return Response(
            content=body,
            status_code=response.status_code,
            headers={
                k: v
                for k, v in response.headers.items()
                if k.lower() not in ["content-encoding", "transfer-encoding"]
            },
        )
    elif get_config().resolve_type == "streaming-proxy":
        response, generator = await streaming_request("GET", data[0].url)
        return StreamingResponse(
            generator,
            status_code=response.status_code,
            headers={
                k: v
                for k, v in response.headers.items()
                if k.lower() not in ["content-encoding", "transfer-encoding"]
            },
        )
