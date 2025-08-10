import urllib.parse
from contextlib import asynccontextmanager
from typing import Optional

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
from ebnr.utils import is_vip


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_config()
    load_cookies()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "EBNR API Running!", "is_vip": await is_vip()}


app.include_router(album_router)
app.include_router(audio_router)
app.include_router(info_router)
app.include_router(meting_router)
app.include_router(playlist_router)
app.include_router(resolve_router)


@app.get("/{link:path}")
async def root_link(link: str, id: Optional[int] = None):
    url = urllib.parse.urlparse(link)
    if url.hostname != "music.163.com" or id is None:
        raise HTTPException(status_code=404, detail="Not Found")
    match url.path:
        case "/album":
            return RedirectResponse(f"/album/{link}?id={id}")
        case "/playlist":
            return RedirectResponse(f"/playlist/{link}?id={id}")
        case "/song":
            return RedirectResponse(f"/info/{link}?id={id}")
        case _:
            raise HTTPException(status_code=404, detail="Not Found")
