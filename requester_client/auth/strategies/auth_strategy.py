from abc import ABC, abstractmethod


class AuthStrategy(ABC):
    """Base class cho mọi loại authentication."""

    @abstractmethod
    def apply(self, headers: dict) -> dict:
        """Cập nhật headers với thông tin auth."""
        pass
