from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from ebnr.config import load_config
from ebnr.core.api import raw
from ebnr.core.cookie import load_cookies
from ebnr.router.album import router as album_router
from ebnr.router.audio import router as audio_router
from ebnr.router.info import router as info_router
from ebnr.router.meting import router as meting_router
from ebnr.router.playlist import router as playlist_router
from ebnr.router.resolve import router as resolve_router

is_vip: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    global is_vip
    load_config()
    load_cookies()
    try:
        data = await raw.user.get_user_info()
    except httpx.RequestError:
        is_vip = False
    else:
        if data["code"] != 200:
            is_vip = False
        else:
            is_vip = data["viptype"] > 0
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "EBNR API Running!", "is_vip": is_vip}


app.include_router(album_router)
app.include_router(audio_router)
app.include_router(info_router)
app.include_router(meting_router)
app.include_router(playlist_router)
app.include_router(resolve_router)
