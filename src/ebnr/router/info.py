from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/info")


@router.api_route("/{path:path}", methods=["GET", "POST", "HEAD"])
async def info(path: str):
    return RedirectResponse(url=f"/song/{path}", status_code=308)
