import os
import tomllib
from asyncio import Semaphore
from dataclasses import dataclass
from typing import Literal


@dataclass
class Config:
    base_url: str
    api_cache: bool
    cache_timeout: int
    audio_cache_timeout: int
    audio_cache_type: Literal["optimistic", "pessimistic"]
    resolve_type: Literal["redirect", "proxy", "streaming-proxy"]
    redirect_code: Literal[302, 307]
    api_semaphore: Semaphore


config = Config(
    base_url="http://127.0.0.1:8000",
    api_cache=True,
    cache_timeout=86400,
    audio_cache_timeout=3600,
    audio_cache_type="optimistic",
    resolve_type="redirect",
    redirect_code=307,
    api_semaphore=Semaphore(200),
)


def load_config():
    global config
    with open("config.toml", "rb") as f:
        config_file = tomllib.load(f)

    base_url = os.environ.get("EBNR_BASE_URL", config_file["base_url"])
    api_cache = (
        str(os.environ.get("EBNR_API_CACHE", config_file["api_cache"])).lower()
        == "true"
    )
    cache_timeout = int(
        os.environ.get("EBNR_CACHE_TIMEOUT", config_file["cache_timeout"])
    )
    audio_cache_timeout = int(
        os.environ.get("EBNR_AUDIO_CACHE_TIMEOUT", config_file["audio_cache_timeout"])
    )
    audio_cache_type = (
        val
        if (
            val := os.environ.get(
                "EBNR_AUDIO_CACHE_TYPE", config_file["audio_cache_type"]
            )
        )
        in ("optimistic", "pessimistic")
        else "pessimistic"
    )
    resolve_type = (
        val
        if (val := os.environ.get("EBNR_RESOLVE_TYPE", config_file["resolve_type"]))
        in ("redirect", "proxy", "streaming-proxy")
        else "redirect"
    )
    redirect_code = (
        val
        if (
            val := int(
                os.environ.get("EBNR_REDIRECT_CODE", config_file["redirect_code"])
            )
        )
        in (302, 307)
        else 307
    )
    api_concurrency = int(
        os.environ.get("EBNR_API_CONCURRENCY", config_file["api_concurrency"])
    )

    config = Config(
        base_url=base_url,
        api_cache=api_cache,
        cache_timeout=cache_timeout,
        audio_cache_timeout=audio_cache_timeout,
        audio_cache_type=audio_cache_type,
        resolve_type=resolve_type,
        redirect_code=redirect_code,
        api_semaphore=Semaphore(api_concurrency),
    )


def get_config():
    return config
