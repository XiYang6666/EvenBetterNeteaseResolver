import json
import weakref
from asyncio import Semaphore
from pathlib import Path
from typing import Optional

from ebnr.core.api import song
from ebnr.core.types import Encoding, Quality


class EbnrSong:
    def __init__(self, parent: "EBNR") -> None:
        self._parent: "EBNR" = weakref.proxy(parent)

    async def get_audio(
        self,
        ids: list[int],
        quality: Quality = Quality.STANDARD,
        encoding: Encoding = Encoding.FLAC,
    ):
        async with self._parent._semaphore:
            return await song.get_audio(
                ids, quality, encoding, cookies=self._parent._cookies
            )

    async def get_song_info(self, ids: list[int]):
        async with self._parent._semaphore:
            return await song.get_song_info(ids, cookies=self._parent._cookies)

    async def get_lyric(self, id: int):
        async with self._parent._semaphore:
            return await song.get_lyric(id, cookies=self._parent._cookies)

    async def search(self, keyword: str, limit: int = 10):
        async with self._parent._semaphore:
            return await song.search(keyword, limit, cookies=self._parent._cookies)

    async def get_playlist(self, id: int):
        async with self._parent._semaphore:
            return await song.get_playlist(id, cookies=self._parent._cookies)

    async def get_tracks(self, id: int, limit: int = 1000, page: int = 0):
        async with self._parent._semaphore:
            return await song.get_tracks(id, limit, page, cookies=self._parent._cookies)

    async def get_album(self, id: int):
        async with self._parent._semaphore:
            return await song.get_album(id, cookies=self._parent._cookies)


class EBNR:
    def __init__(
        self,
        *,
        cookies: Optional[dict[str, str]] = None,
        semaphore: Semaphore = Semaphore(200),
    ):
        self._cookies = cookies
        self._semaphore = semaphore
        self.song = EbnrSong(self)

    def load_cookies_json(self, path: Path | str):
        with open(path, "r", encoding="utf-8") as f:
            self._cookies = json.load(f)

    def set_cookies(self, cookies: dict[str, str]):
        self._cookies = cookies
