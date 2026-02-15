from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, Mapping, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from ebnr.config import load_config
from ebnr.core.cookie import load_cookies
from ebnr.router.album import router as album_router
from ebnr.router.audio import router as audio_router
from ebnr.router.info import router as info_router
from ebnr.router.meting import router as meting_router
from ebnr.router.playlist import router as playlist_router
from ebnr.router.resolve import router as resolve_router
from ebnr.router.search import router as search_router
from ebnr.router.tracks import router as tracks_router
from ebnr.utils import is_vip, parse_netease_link

COOKIE_PATH = Path("data/cookie.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not COOKIE_PATH.exists():
        COOKIE_PATH.write_text("{}", encoding="utf-8")

    load_config()
    load_cookies(COOKIE_PATH)
    yield


app = FastAPI(lifespan=lifespan, title="Even Better Netease Resolver (EBNR)")


@app.get("/")
async def root():
    """显示欢迎信息与 VIP 状态"""
    return {"message": "EBNR API Running!", "is_vip": await is_vip()}


app.include_router(info_router)
app.include_router(audio_router)
app.include_router(resolve_router)
app.include_router(playlist_router)
app.include_router(tracks_router)
app.include_router(album_router)
app.include_router(search_router)
app.include_router(meting_router)


@app.get("/{link:path}", response_class=RedirectResponse)
async def root_link(link: str, id: Optional[int] = None):
    """自动根据传入的网易云音乐链接重定向至对应的路由"""
    link_info = parse_netease_link(link, id)
    if link_info is None:
        raise HTTPException(status_code=404, detail="Not Found")
    type_mapping: Mapping[Literal["song", "album", "playlist"], str] = {
        "song": "info",
        "album": "album",
        "playlist": "playlist",
    }
    return RedirectResponse(f"/{type_mapping[link_info.type]}/{link_info.url}")
