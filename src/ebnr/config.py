import os
import tomllib
from dataclasses import dataclass


@dataclass
class Config:
    concurrency_resolve_playlist: int
    base_url: str
    api_cache: bool
    audio_cache_timeout: int


config: Config = Config(
    concurrency_resolve_playlist=10,
    base_url="http://localhost:8000",
    api_cache=True,
    audio_cache_timeout=3600,
)


def load_config():
    global config
    with open("config.toml", "rb") as f:
        config_file = tomllib.load(f)

    config = Config(
        concurrency_resolve_playlist=int(
            os.environ.get(
                "EBNR_CONCURRENCY_RESOLVE_PLAYLIST",
                config_file["concurrency_resolve_playlist"],
            )
        ),
        base_url=os.environ.get(
            "EBNR_BASE_URL",
            config_file["base_url"],
        ),
        api_cache=os.environ.get(
            "EBNR_API_CACHE",
            str(config_file["api_cache"]),
        ).lower()
        == "true",
        audio_cache_timeout=int(
            os.environ.get(
                "EBNR_AUDIO_CACHE_TIMEOUT",
                config_file["audio_cache_timeout"],
            )
        ),
    )


def get_config():
    return config
