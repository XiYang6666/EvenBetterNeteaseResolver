import asyncio
from asyncio import Semaphore
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, RedirectResponse

from ebnr.config import get_config
from ebnr.core.types import SongInfo
from ebnr.services.cached_api.song import (
    get_audio,
    get_lyric,
    get_playlist,
    get_song_info,
)
from ebnr.utils import with_semaphore

router = APIRouter(prefix="/meting")


@router.api_route("/", methods=["GET", "HEAD"])
async def meting(type: str, id: int, server: Optional[str] = None):
    if server is not None and server != "netease":
        raise HTTPException(400, "Unsupported Server")
    if type == "song":
        if (
            not (song_info_list := await get_song_info([id]))
            or not song_info_list[0]
            or not (url_info_list := await get_audio([id]))
        ):
            raise HTTPException(404, "Song Not Found")
        url_info = url_info_list[0]
        song_info = song_info_list[0]
        return [
            {
                "name": song_info.name,
                "artist": "/".join([artist.name for artist in song_info.artists]),
                "url": url_info and url_info.url,
                "pic": song_info.album and song_info.album.cover_url,
                "lrc": get_config().base_url + f"/meting/?type=lrc&id={id}",
            }
        ]
    elif type == "url":
        if not (url_info_list := await get_audio([id])) or not url_info_list[0]:
            raise HTTPException(404, "Song Not Found")
        url_info = url_info_list[0]
        if not url_info.url:
            raise HTTPException(400, "Song Not Available")
        return RedirectResponse(url_info.url)
    elif type == "lrc":
        if not (lrc_info := await get_lyric(id)):
            raise HTTPException(404, "Lrc Not Found")
        lyric = lrc_info.translated_lyric or lrc_info.original_lyric
        return PlainTextResponse(lyric.lyric if lyric else "")
    elif type == "playlist":
        if not (palylist_info := await get_playlist(id)):
            raise HTTPException(404, "Playlist Not Found")

        semaphore = Semaphore(get_config().concurrency_resolve_playlist)

        @with_semaphore(semaphore)
        async def resolve_track(track: SongInfo):
            return (
                {
                    "name": track.name,
                    "url": url_info[0].url,
                    "artist": "/".join([artist.name for artist in track.artists]),
                    "pic": track.album and track.album.cover_url,
                    "lrc": f"{get_config().base_url}/meting/?type=lrc&id={track.id}",
                }
                if (url_info := await get_audio([track.id])) and url_info[0]
                else None
            )

        tasks = [resolve_track(track) for track in palylist_info.tracks]
        result = list(filter(lambda x: x is not None, await asyncio.gather(*tasks)))
        return result
    else:
        raise HTTPException(400, "Unsupported Type")
