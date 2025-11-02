import httpx
import asyncio
import time
from io import BytesIO
from typing import Optional, Any, Dict, Union, Callable

from requester_client.utils.json_helper import get_nested_key
from requester_client.auth.auth_strategy import AuthStrategy
from requester_client.auth.no_auth import NoAuth
from requester_client.rate_limiter.base_rate_limiter import BaseRateLimiter
from requester_client.rate_limiter.header_rate_limiter import HeaderRateLimiter

class DynamicHttpClient:
    """
    HTTP client động hỗ trợ:
    - Auth (Bearer, Basic, API Key)
    - Retry + backoff
    - Rate limit header-based
    - Pagination (next_page_key dạng nested hoặc callable)
    """

    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Dict[str, str]] = None,
        auth_strategy: Optional[AuthStrategy] = None,
        rate_limiter: Optional[BaseRateLimiter] = None,
        retry_count: int = 3,
        retry_backoff_factor: float = 0.5,
        status_forcelist: Optional[list[int]] = None,
    ):
        self.base_url = base_url
        self.headers = headers or {}
        self.auth_strategy = auth_strategy or NoAuth()
        self.rate_limiter = rate_limiter or HeaderRateLimiter()
        self.retry_count = retry_count
        self.retry_backoff_factor = retry_backoff_factor
        self.status_forcelist = status_forcelist or [429, 500, 502, 503, 504]

        self.sync_client = httpx.Client(base_url=base_url, headers=self._auth_headers())
        self.async_client = httpx.AsyncClient(base_url=base_url, headers=self._auth_headers())

    # -------------------------------
    # Internal Helpers
    # -------------------------------
    def _auth_headers(self) -> dict:
        """Áp dụng auth vào headers hiện tại."""
        return self.auth_strategy.apply(self.headers.copy())

    def _extract_next_token(self, data: dict, next_page_key: Union[str, Callable[[dict], Any]]) -> Any:
        """Lấy token/trang tiếp theo từ data."""
        if callable(next_page_key):
            return next_page_key(data)
        elif isinstance(next_page_key, str):
            return get_nested_key(data, next_page_key)
        return None

    # -------------------------------
    # Core Sync Request
    # -------------------------------
    def request_sync(self, method: str, url: str, **kwargs) -> Optional[httpx.Response]:
        for attempt in range(1, self.retry_count + 1):
            try:
                response = self.sync_client.request(method, url, **kwargs)
                if response.status_code in self.status_forcelist:
                    print(f"[Retry] Attempt {attempt}: HTTP {response.status_code}")
                    if response.status_code == 429:
                        asyncio.run(self.rate_limiter.handle_rate_limit(response))
                    time.sleep(self.retry_backoff_factor * attempt)
                    continue
                response.raise_for_status()
                return response
            except httpx.RequestError as e:
                print(f"[Error] Request failed: {e}")
                time.sleep(self.retry_backoff_factor * attempt)
        return None

    # -------------------------------
    # Core Async Request
    # -------------------------------
    async def request_async(self, method: str, url: str, **kwargs) -> Optional[httpx.Response]:
        for attempt in range(1, self.retry_count + 1):
            try:
                response = await self.async_client.request(method, url, **kwargs)
                if response.status_code in self.status_forcelist:
                    print(f"[Retry] Attempt {attempt}: HTTP {response.status_code}")
                    if response.status_code == 429:
                        await self.rate_limiter.handle_rate_limit(response)
                    await asyncio.sleep(self.retry_backoff_factor * attempt)
                    continue
                response.raise_for_status()
                return response
            except httpx.RequestError as e:
                print(f"[Error] Request failed: {e}")
                await asyncio.sleep(self.retry_backoff_factor * attempt)
        return None

    # -------------------------------
    # Pagination
    # -------------------------------
    async def paginate_async(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        next_page_key: Union[str, Callable[[dict], Any]] = "next",
        extract_items: Optional[Callable[[dict], list]] = None,
        page_token_param: str = "page_token",
    ):
        params = params or {}
        next_token = None
        while True:
            if next_token:
                params[page_token_param] = next_token
            resp = await self.request_async(method, endpoint, params=params)
            if not resp:
                break
            data = resp.json()
            items = extract_items(data) if extract_items else data.get("results", [])
            yield items
            next_token = self._extract_next_token(data, next_page_key)
            if not next_token:
                break

    def paginate_sync(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        next_page_key: Union[str, Callable[[dict], Any]] = "next",
        extract_items: Optional[Callable[[dict], list]] = None,
        page_token_param: str = "page_token",
    ):
        params = params or {}
        next_token = None
        while True:
            if next_token:
                params[page_token_param] = next_token
            resp = self.request_sync(method, endpoint, params=params)
            if not resp:
                break
            data = resp.json()
            items = extract_items(data) if extract_items else data.get("results", [])
            yield items
            next_token = self._extract_next_token(data, next_page_key)
            if not next_token:
                break

    # -------------------------------
    # Convenience Methods
    # -------------------------------
    def get_sync(self, url, **kwargs):
        return self.request_sync("GET", url, **kwargs)

    def post_sync(self, url, **kwargs):
        return self.request_sync("POST", url, **kwargs)

    async def get_async(self, url, **kwargs):
        return await self.request_async("GET", url, **kwargs)

    async def post_async(self, url, **kwargs):
        return await self.request_async("POST", url, **kwargs)

    # -------------------------------
    # Context Manager
    # -------------------------------
    def close(self):
        self.sync_client.close()

    async def aclose(self):
        await self.async_client.aclose()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.aclose()