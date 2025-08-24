from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Optional


class Quality(StrEnum):
    # 标准音质
    STANDARD = "standard"
    # 极高音质
    EXHIGH = "exhigh"
    # 无损音质
    LOSSLESS = "lossless"
    # Hires音质
    HIRES = "hires"
    # 沉浸环绕声
    SKY = "sky"
    # 高清环绕声
    JYEFFECT = "jyeffect"
    # 超清母带
    JYMASTER = "jymaster"


class Encoding(StrEnum):
    # MP3编码
    MP3 = "mp3"
    # FLAC编码
    FLAC = "flac"


@dataclass
class AudioData:
    id: int
    url: Optional[str]
    # 编码
    encoding: Optional[Encoding]
    # 比特率
    bitrate: int
    # 文件大小
    size: int
    md5: str
    # 时长(毫秒)
    duration: int
    # 采样率
    sample_rate: int
    # 响度增益
    gain: float
    # 音频峰值
    peak: float
    # 是否已付费
    payed: bool
    # 是否付费
    fee: bool


@dataclass
class ArtistShort:
    id: int
    name: str
    translations: Optional[list[str]]
    alias: Optional[list[str]]


@dataclass
class AlbumShort:
    id: int
    name: str
    translations: Optional[list[str]]
    cover_url: Optional[str]


@dataclass
class QualityInfo:
    # 比特率
    bitrate: int
    # 文件大小
    size: int
    # 采样率
    sample_rate: Optional[int]


@dataclass
class Qualities:
    # 标准音质(l)
    standard: Optional[QualityInfo]
    # 极高音质(h)
    exhigh: Optional[QualityInfo]
    # 无损音质(sq)
    lossless: Optional[QualityInfo]
    # Hires音质(hr)
    hires: Optional[QualityInfo]
    # 沉浸环绕声
    sky: Optional[QualityInfo]
    # 高清环绕声
    jyeffect: Optional[QualityInfo]
    # 超清母带()
    jymaster: Optional[QualityInfo]


@dataclass
class SongInfo:
    id: int
    name: str
    main_title: Optional[str]
    additional_title: Optional[str]
    translations: Optional[list[str]]
    alias: Optional[list[str]]
    # 流行度(0-100)
    pop: float
    # 艺术家
    artists: list[ArtistShort]
    # 专辑
    album: Optional[AlbumShort]
    # MV id
    music_video_id: Optional[int]
    # 发布时间
    publish_time: Optional[datetime]
    # 质量
    qualities: Qualities


@dataclass
class LyricContributor:
    id: int
    user_id: int
    nickname: str
    update_time: int


@dataclass
class LyricContent:
    version: int
    lyric: str


@dataclass
class LyricData:
    lyric_contributor: Optional[LyricContributor]
    translation_contributor: Optional[LyricContributor]

    original_lyric: Optional[LyricContent]
    translated_lyric: Optional[LyricContent]
    romaji_lyric: Optional[LyricContent]
    karaoke_lyric: Optional[LyricContent]
    word_by_word_lyric: Optional[LyricContent]


@dataclass
class PlaylistCreator:
    user_id: int
    nickname: str
    signature: str
    avatar_url: str
    background_url: str
    city_code: int


@dataclass
class Playlist:
    id: int
    name: str
    description: Optional[str]
    cover_url: str
    track_count: int
    play_count: int
    creator: Optional[PlaylistCreator]
    tracks: list[SongInfo]


@dataclass
class Artist(ArtistShort):
    picture_url: str


@dataclass
class Album(AlbumShort):
    alias: Optional[list[str]]
    description: Optional[str]
    artists: list[ArtistShort]
    songs: list[SongInfo]


@dataclass
class UserShort:
    nickname: str
    avatar_url: str


class QrcodeStatus(IntEnum):
    # 等待扫码
    WAITING = 801
    # 授权中
    AUTHORIZING = 802
    # 授权成功
    AUTHORIZED = 803
    # 需要验证码
    NEED_CAPTCHA = 8821
