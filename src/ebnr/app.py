from contextlib import asynccontextmanager

from fastapi import FastAPI

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
