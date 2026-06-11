from typing import Literal

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

type AudioCacheValidationTypeType = Literal["sync", "background"]
type ResolveResponseTypeType = Literal["redirect", "proxy", "streaming-proxy"]
type RedirectCodeType = Literal[302, 307]


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file="config.toml",
        env_prefix="EBNR_",
        env_ignore_empty=True,
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
    api_cache: bool = True
    cache_size: int = 1024
    cache_timeout: int = 86400
    audio_cache_timeout: int = 3600
    audio_cache_validation_type: AudioCacheValidationTypeType = "background"
    resolve_response_type: ResolveResponseTypeType = "redirect"
    redirect_code: Literal[302, 307] = 307
    api_concurrency: int = 200


config = None


def load_config():
    global config
    config = Config()


def get_config():
    assert config is not None
    return config
