from datetime import datetime
from typing import Any

from ebnr.core.types import (
    Album,
    AlbumShort,
    Artist,
    ArtistShort,
    AudioInfo,
    Encoding,
    LyricContent,
    LyricContributor,
    LyricData,
    Playlist,
    PlaylistCreator,
    Qualities,
    QualityInfo,
    SongInfo,
)
from ebnr.core.utils import fix_song_url


def parse_audio_json(data: dict[str, Any]) -> AudioInfo:
    return AudioInfo(
        id=data["id"],
        url=(url := data.get("url")) and fix_song_url(url),
        encoding=Encoding(data["type"]) if data.get("type") else None,
        bitrate=data["br"],
        size=data["size"],
        md5=data["md5"],
        duration=data["time"],
        sample_rate=data["sr"],
        gain=data["gain"],
        peak=data["peak"],
        payed=data["payed"] != 0,
        fee=data["fee"] != 0,
    )


def parse_song_json(data: dict[str, Any]) -> SongInfo:
    return SongInfo(
        id=data["id"],
        name=data["name"],
        main_title=data.get("mainTitle"),
        additional_title=data.get("additionalTitle"),
        translations=data.get("tns"),
        alias=data.get("alia"),
        pop=data["pop"],
        artists=[
            ArtistShort(
                id=artist["id"],
                name=artist["name"],
                translations=artist.get("tns"),
                alias=artist.get("alias"),
            )
            for artist in data["ar"]
        ],
        album=AlbumShort(
            id=data["al"]["id"],
            name=data["al"]["name"],
            translations=data["al"].get("tns"),
            cover_url=data["al"].get("picUrl"),
        )
        if data.get("al")
        else None,
        music_video_id=data["mv"] or None,
        publish_time=datetime.fromtimestamp(data["publishTime"] / 1000)
        if data.get("publishTime")
        else None,
        qualities=Qualities(
            standard=QualityInfo(
                bitrate=data["l"]["br"],
                size=data["l"]["size"],
                sample_rate=data["l"].get("sr"),
            )
            if data.get("l")
            else None,
            exhigh=QualityInfo(
                bitrate=data["h"]["br"],
                size=data["h"]["size"],
                sample_rate=data["h"].get("sr"),
            )
            if data.get("h")
            else None,
            lossless=QualityInfo(
                bitrate=data["sq"]["br"],
                size=data["sq"]["size"],
                sample_rate=data["sq"].get("sr"),
            )
            if data.get("sq")
            else None,
            hires=QualityInfo(
                bitrate=data["hr"]["br"],
                size=data["hr"]["size"],
                sample_rate=data["hr"].get("sr"),
            )
            if data.get("hr")
            else None,
            sky=None,
            jyeffect=None,
            jymaster=None,
        ),
    )


def parse_lyric_json(data: dict[str, Any]) -> LyricData:
    return LyricData(
        lyric_contributor=LyricContributor(
            id=data["lyricUser"]["id"],
            user_id=data["lyricUser"]["userid"],
            nickname=data["lyricUser"]["nickname"],
            update_time=data["lyricUser"]["uptime"],
        )
        if data.get("lyricUser")
        else None,
        translation_contributor=LyricContributor(
            id=data["transUser"]["id"],
            user_id=data["transUser"]["userid"],
            nickname=data["transUser"]["nickname"],
            update_time=data["transUser"]["uptime"],
        )
        if data.get("transUser")
        else None,
        original_lyric=LyricContent(
            version=data["lrc"]["version"],
            lyric=data["lrc"]["lyric"],
        )
        if data.get("lrc")
        else None,
        translated_lyric=LyricContent(
            version=data["tlyric"]["version"],
            lyric=data["tlyric"]["lyric"],
        )
        if data.get("tlyric")
        else None,
        romaji_lyric=LyricContent(
            version=data["romalrc"]["version"],
            lyric=data["romalrc"]["lyric"],
        )
        if data.get("romalrc")
        else None,
        karaoke_lyric=LyricContent(
            version=data["klyric"]["version"],
            lyric=data["klyric"]["lyric"],
        )
        if data.get("klyric")
        else None,
        word_by_word_lyric=LyricContent(
            version=data["yrc"]["version"],
            lyric=data["yrc"]["lyric"],
        )
        if data.get("yrc")
        else None,
    )


def parse_playlist_json(data: dict[str, Any]) -> Playlist:
    return Playlist(
        id=data["id"],
        name=data["name"],
        description=data.get("description"),
        cover_url=data["coverImgUrl"],
        track_count=data["trackCount"],
        play_count=data["playCount"],
        creator=PlaylistCreator(
            user_id=data["creator"]["userId"],
            nickname=data["creator"]["nickname"],
            signature=data["creator"]["signature"],
            avatar_url=data["creator"]["avatarUrl"],
            background_url=data["creator"]["backgroundUrl"],
            city_code=data["creator"]["city"],
        )
        if data.get("creator")
        else None,
        tracks=[parse_song_json(track) for track in data["tracks"]],
    )


def parse_album_json(data: dict[str, Any]) -> Album:
    return Album(
        id=data["album"]["id"],
        name=data["album"]["name"],
        translations=data["album"].get("transNames"),
        alias=data["album"].get("alias"),
        description=data["album"].get("description"),
        artists=[
            Artist(
                id=artist["id"],
                name=artist["name"],
                translations=[artist["trans"]] if artist.get("trans") else None,
                alias=artist["alias"] if artist.get("alias") else None,
                picture_url=artist["picUrl"],
            )
            for artist in data["album"]["artists"]
        ],
        cover_url=data["album"]["picUrl"],
        songs=[parse_song_json(song) for song in data["songs"]],
    )
