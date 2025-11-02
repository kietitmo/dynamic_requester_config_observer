from abc import ABC, abstractmethod

class BaseConfigProvider(ABC):
    """Base interface cho các config provider."""

    @abstractmethod
    def load(self) -> dict:
        """Trả về raw config dưới dạng dict."""
        pass
