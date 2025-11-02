import httpx
from abc import ABC, abstractmethod


class BaseRateLimiter(ABC):
    """Base class cho rate limiter."""

    @abstractmethod
    async def handle_rate_limit(self, response: httpx.Response):
        pass