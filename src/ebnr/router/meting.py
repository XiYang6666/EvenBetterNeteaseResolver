import urllib.parse
from dataclasses import dataclass
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

router = APIRouter(prefix="/meting", tags=["meting-api 兼容接口"])


@dataclass
class MetingResult:
    name: str
    artist: str
    url: Optional[str]
    pic: Optional[str]
    lrc: str

    @classmethod
    def from_song_info(cls, song_info: SongInfo):
        return cls(
            name=song_info.name,
            artist="/".join([artist.name for artist in song_info.artists]),
            url=get_config().base_url + f"/meting/?type=url&id={id}",
            pic=song_info.album and song_info.album.cover_url,
            lrc=get_config().base_url + f"/meting/?type=lrc&id={id}",
        )


@router.get("/")
@router.head("/", include_in_schema=False)
async def meting(type: str, id: int, server: Optional[str] = None):
    """
    meting-api 兼容接口, 详见 [meting-api](https://github.com/injahow/meting-api)
    """
    if server is not None and server != "netease":
        raise HTTPException(400, "Unsupported Server")
    if type == "song":
        if not (song_info := await get_song_info([id])) or not song_info[0]:
            raise HTTPException(404, "Song Not Found")
        return [MetingResult.from_song_info(song_info[0])]
    elif type == "url":
        url_info = await get_audio([id])
        if not url_info:
            raise HTTPException(404, "Song Not Found")
        if not url_info[0]:
            raise HTTPException(404, "Could Not Get Audio")
        if not url_info[0].url and url_info[0].fee and not url_info[0].payed:
            raise HTTPException(404, "VIP Song")
        if not url_info[0].url:
            raise HTTPException(404, "Audio Not Available")
        return RedirectResponse(url_info[0].url)
    elif type == "lrc":
        if not (lrc_info := await get_lyric(id)):
            raise HTTPException(404, "Lrc Not Found")
        lyric = lrc_info.translated_lyric or lrc_info.original_lyric
        return PlainTextResponse(lyric.lyric if lyric else "")
    elif type == "playlist":
        if not (playlist_info := await get_playlist(id)):
            raise HTTPException(404, "Playlist Not Found")
        result = [MetingResult.from_song_info(track) for track in playlist_info.tracks]
        return result
    else:
        raise HTTPException(400, "Unsupported Type")


@router.api_route("", methods=["GET", "HEAD"], include_in_schema=False)
async def redirect(type: str, id: int):
    return RedirectResponse(
        f"/meting/?{urllib.parse.urlencode({'type': type, 'id': id})}"
    )
