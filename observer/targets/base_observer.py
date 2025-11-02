from typing import Any, Dict

class BaseObserver:
    def __init__(self, name: str, config: dict | None = None):
        self.name = name
        self.config = config or {}

    async def update(self, message: Dict[str, Any]):
        """Gửi message đến nơi cần thiết (override ở subclass)."""
        raise NotImplementedError
