import os
import tomllib
from dataclasses import dataclass
from typing import Callable, Literal, TypeGuard, cast

from ebnr.utils import first_not_none, maybe_apply, validate_with_fallback

type AudioCacheValidationTypeType = Literal["sync", "background"]
type ResolveResponseTypeType = Literal["redirect", "proxy", "streaming-proxy"]
type RedirectCodeType = Literal[302, 307]


@dataclass
class Config:
    base_url: str
    api_cache: bool
    cache_size: int
    cache_timeout: int
    audio_cache_timeout: int
    audio_cache_validation_type: AudioCacheValidationTypeType
    resolve_response_type: ResolveResponseTypeType
    redirect_code: Literal[302, 307]
    api_concurrency: int


config = Config(
    base_url="http://127.0.0.1:8000",
    api_cache=True,
    cache_size=1024,
    cache_timeout=86400,
    audio_cache_timeout=3600,
    audio_cache_validation_type="background",
    resolve_response_type="redirect",
    redirect_code=307,
    api_concurrency=200,
)


def load_config():
    global config
    with open("config.toml", "rb") as f:
        config_file = tomllib.load(f)

    base_url = (
        os.environ.get("EBNR_BASE_URL")
        or cast(str, config_file["base_url"])
        or "http://127.0.0.1:8000"
    )
    api_cache = first_not_none(
        lambda: maybe_apply(
            os.environ.get("EBNR_API_CACHE"), lambda x: x.lower() == "true"
        ),
        lambda: cast(bool, config_file["api_cache"]),
        lambda: True,
    )
    cache_size = (
        maybe_apply(os.environ.get("EBNR_CACHE_SIZE"), int)
        or cast(int, config_file["cache_size"])
        or 1024
    )
    cache_timeout = (
        maybe_apply(os.environ.get("EBNR_CACHE_TIMEOUT"), int)
        or cast(int, config_file["cache_timeout"])
        or 86400
    )
    audio_cache_timeout = (
        maybe_apply(os.environ.get("EBNR_AUDIO_CACHE_TIMEOUT"), int)
        or cast(int, config_file["audio_cache_timeout"])
        or 3600
    )
    audio_cache_validation_type: AudioCacheValidationTypeType = validate_with_fallback(
        os.environ.get("EBNR_AUDIO_CACHE_VALIDATION_TYPE")
        or cast(
            AudioCacheValidationTypeType,
            config_file["audio_cache_validation_type"],
        )
        or "background",
        cast(
            Callable[[str], TypeGuard[AudioCacheValidationTypeType]],
            lambda x: x in ("sync", "background"),
        ),
        "background",
    )
    resolve_response_type: ResolveResponseTypeType = validate_with_fallback(
        os.environ.get("EBNR_RESOLVE_RESPONSE_TYPE")
        or cast(
            ResolveResponseTypeType,
            config_file["resolve_response_type"],
        )
        or "redirect",
        cast(
            Callable[[str], TypeGuard[ResolveResponseTypeType]],
            lambda x: x in ("redirect", "proxy", "streaming-proxy"),
        ),
        "redirect",
    )
    redirect_code: RedirectCodeType = validate_with_fallback(
        maybe_apply(os.environ.get("EBNR_REDIRECT_CODE"), int)
        or cast(int, config_file["redirect_code"])
        or 307,
        cast(Callable[[int], TypeGuard[RedirectCodeType]], lambda x: x in (302, 307)),
        307,
    )
    api_concurrency = (
        maybe_apply(os.environ.get("EBNR_API_CONCURRENCY"), int)
        or cast(int, config_file["api_concurrency"])
        or 200
    )

    config = Config(
        base_url=base_url,
        api_cache=api_cache,
        cache_size=cache_size,
        cache_timeout=cache_timeout,
        audio_cache_timeout=audio_cache_timeout,
        audio_cache_validation_type=audio_cache_validation_type,
        resolve_response_type=resolve_response_type,
        redirect_code=redirect_code,
        api_concurrency=(api_concurrency),
    )


def get_config():
    return config
