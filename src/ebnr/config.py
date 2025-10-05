import os
import tomllib
from dataclasses import dataclass
from typing import Literal


@dataclass
class Config:
    base_url: str
    api_cache: bool
    audio_cache_timeout: int
    audio_cache_type: Literal["optimistic", "pessimistic"]
    redirect_code: Literal[302, 307]


config: Config = Config(
    base_url="http://localhost:8000",
    api_cache=True,
    audio_cache_timeout=3600,
    audio_cache_type="optimistic",
    redirect_code=307,
)


def load_config():
    global config
    with open("config.toml", "rb") as f:
        config_file = tomllib.load(f)

    base_url = os.environ.get("EBNR_BASE_URL", config_file["base_url"])
    api_cache = (
        str(os.environ.get("EBNR_API_CACHE", config_file["api_cache"])).lower() == "true"
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

    config = Config(
        base_url=base_url,
        api_cache=api_cache,
        audio_cache_timeout=audio_cache_timeout,
        audio_cache_type=audio_cache_type,
        redirect_code=redirect_code,
    )


def get_config():
    return config
