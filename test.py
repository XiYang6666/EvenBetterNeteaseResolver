import asyncio
import os
import sys

from ebnr.services.cached_api.song import get_album

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "./src")))

from ebnr.core.api.song import get_audio, get_lyric, get_playlist, get_song_info


async def main():
    # https://music.163.com/song?id=1357953770&uct2=U2FsdGVkX189E5wj9hJWLwQmYGLfNQ4e//SBtlbJOOU=
    # song_info = await get_song_info([1357953770])
    # print(song_info)

    # audio_data = await get_audio([1357953770])
    # print(audio_data)

    lyric_data = await get_lyric(1115465465465456)
    print(lyric_data)

    # playlist_info = await get_playlist(12345644545645)
    # print(playlist_info)

    album_info = await get_album(12345644545645)
    print(album_info)


if __name__ == "__main__":
    asyncio.run(main())
