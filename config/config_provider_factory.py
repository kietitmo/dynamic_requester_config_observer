import os
from .providers.env_config_provider import EnvConfigProvider
from .providers.base_config_provider import BaseConfigProvider

def get_config_provider() -> BaseConfigProvider:
    provider_type = os.getenv("CONFIG_PROVIDER", "env").lower()
    if provider_type == "env":
         EnvConfigProvider()
    else:
        raise ValueError(f"Unknown CONFIG_PROVIDER: {provider_type}")
    return EnvConfigProvider()

def load_raw_config() -> dict:
    provider = get_config_provider()
    raw = provider.load()
    print(f"[CONFIG] Loaded raw config from {provider.__class__.__name__}")
    return raw

def reload_raw_config() -> dict:
    load_raw_config.cache_clear()
    return load_raw_config()
