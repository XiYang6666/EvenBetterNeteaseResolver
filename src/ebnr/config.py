from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = Field(default=6379, ge=0, le=65535)
    db: int = Field(default=0, ge=0, le=15)
    username: Optional[str] = None
    password: Optional[str] = None
    prefix: str = "ebnr:"
    max_connections: int = 50


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file="config/config.toml",
        env_prefix="EBNR_",
        env_ignore_empty=True,
        env_nested_delimiter="_",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )

    base_url: str = "http://127.0.0.1:8000"

    netease_cookie: Optional[dict[str, str]] = Field(default=None, exclude=True)
    cookie_file_path: str = Field(default="./data/cookie.json", exclude=True)
    cookie_file_type: Literal["object", "list"] = "object"

    api_cache: bool = True
    cache_size: int = 1024
    cache_timeout: int = 86400
    cache_backend: Literal["memory", "redis"] = "memory"
    cache_fallback: bool = False

    audio_cache_timeout: int = 3600
    audio_cache_validation_type: Literal["sync", "background"] = "background"

    resolve_response_type: Literal["redirect", "proxy", "streaming-proxy"] = "redirect"
    redirect_code: Literal[302, 307] = 307
    api_concurrency: int = 200

    redis: RedisConfig = Field(default_factory=RedisConfig, exclude=True)


config = None


def load_config():
    global config
    config = Config()


def get_config():
    assert config is not None
    return config
