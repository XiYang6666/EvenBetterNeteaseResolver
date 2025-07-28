from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from ebnr.core.api.song import get_audio

router = APIRouter(prefix="/resolve")


@router.get("/{link:path}")
async def resolve_link(link: str, id: int):
    if link != "https://music.163.com/song":
        raise HTTPException(400, "Invalid Link")
    data = await get_audio([id])
    if not data:
        raise HTTPException(404, "Song Not Found")
    return RedirectResponse(data[0].url)
