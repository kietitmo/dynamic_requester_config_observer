import os
import json
from .base_config_provider import BaseConfigProvider

class EnvConfigProvider(BaseConfigProvider):
    """
    Provider đọc config từ ENV, hỗ trợ prefix theo môi trường:
    DEV_, TEST_, PROD_, STAGING_...
    """

    PREFIX_MAP = {
        "dev": "DEV_",
        "test": "TEST_",
        "prod": "PROD_",
        "staging": "STAGING_",
    }

    def __init__(self):
        self.env = os.getenv("APP_ENV", "dev").lower()
        self.prefix = self.PREFIX_MAP.get(self.env, f"{self.env.upper()}_")
        print(f"[CONFIG] EnvConfigProvider using prefix: {self.prefix}")
        self.config = self._load_all()

    def _parse_json_env(self, key: str) -> dict:
        """Đọc và parse biến ENV (ưu tiên theo prefix môi trường)."""
        prefixed_key = f"{self.prefix}{key}"
        raw = os.getenv(prefixed_key) or os.getenv(key) or "{}"
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON in {prefixed_key or key}")
            return {}

    def _load_all(self) -> dict:
        """Load toàn bộ config nhóm từ ENV."""
        configs = {
            "observer": self._parse_json_env("OBSERVER_CONFIG"),
            "data_source": self._parse_json_env("DATA_SOURCE_CONFIG"),
            "message_queue": self._parse_json_env("MESSAGE_QUEUE_CONFIG"),
            "environment": self.env,
        }
        return configs

    def load(self) -> dict:
        """Public API load config."""
        return self.config
