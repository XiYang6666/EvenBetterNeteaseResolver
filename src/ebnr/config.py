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


config: Config = Config(
    base_url="http://localhost:8000",
    api_cache=True,
    audio_cache_timeout=3600,
    audio_cache_type="optimistic",
)


def load_config():
    global config
    with open("config.toml", "rb") as f:
        config_file = tomllib.load(f)

    base_url = os.environ.get(
        "EBNR_BASE_URL",
        config_file["base_url"],
    )
    api_cache = (
        val.lower() == "true"
        if (val := os.environ.get("EBNR_API_CACHE")) is not None
        else config_file["api_cache"]
    )
    audio_cache_timeout = (
        int(val)
        if (val := os.environ.get("EBNR_AUDIO_CACHE_TIMEOUT")) is not None
        else config_file["audio_cache_timeout"]
    )
    audio_cache_type = (
        val
        if (
            val := os.environ.get(
                "EBNR_AUDIO_CACHE_TYPE",
                config_file["audio_cache_type"],
            )
        )
        in ("optimistic", "pessimistic")
        else "pessimistic"
    )

    config = Config(
        base_url=base_url,
        api_cache=api_cache,
        audio_cache_timeout=audio_cache_timeout,
        audio_cache_type=audio_cache_type,
    )


def get_config():
    return config
