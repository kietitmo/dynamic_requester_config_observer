from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from config.models import ObserverConfig, DataSourceConfig, MessageQueueConfig
from config.config_provider_factory import load_raw_config

class AppSettings(BaseSettings):
    """Lớp chính cho toàn bộ app settings (typed-safe)."""

    observer: ObserverConfig = Field(default_factory=ObserverConfig)
    data_source: DataSourceConfig = Field(default_factory=DataSourceConfig)
    message_queue: MessageQueueConfig = Field(default_factory=MessageQueueConfig)

    @classmethod
    def load(cls) -> "AppSettings":
        """Tạo AppSettings từ raw config provider."""
        raw = load_raw_config()
        return cls(**raw)

@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Singleton, thread-safe."""
    return AppSettings.load()

# Singleton settings
settings = AppSettings.load()
