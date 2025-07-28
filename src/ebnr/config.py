import os
import tomllib
from dataclasses import dataclass


@dataclass
class Config:
    concurrency_resolve_playlist: int
    base_url: str


config: Config


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
    )


def get_config():
    return config
