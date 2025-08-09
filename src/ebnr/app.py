from contextlib import asynccontextmanager

import httpx
from cachetools import TTLCache
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

is_vip_cache = TTLCache(maxsize=1, ttl=60 * 60 * 24)


async def is_vip() -> bool:
    if is_vip_cache.get("is_vip") is not None:
        return is_vip_cache["is_vip"]
    try:
        data = await raw.user.get_user_info()
    except httpx.RequestError:
        is_vip_cache["is_vip"] = False
        return False
    else:
        result = data["code"] == 200 and data.get("account", {}).get("vipType", 0) > 0
        is_vip_cache["is_vip"] = result
        return result


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_config()
    load_cookies()
    is_vip_cache["is_vip"] = await is_vip()
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
