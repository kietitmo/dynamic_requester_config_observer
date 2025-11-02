import asyncio
from typing import Any
from observer.base_observer import BaseObserver
from requester_client.dynamic_http_client import DynamicHttpClient
from requester_client.auth.auth_factory import build_auth_strategy
from requester_client.rate_limiter.rate_limiter_factory import create_rate_limiter


class HttpTarget(BaseObserver):
    """Target HTTP gửi data đi async, hỗ trợ auth, retry, ratelimit."""

    def __init__(self, config: dict):
        super().__init__(name=config.get("name", "http_target"), config=config)
        self.urls = config.get("urls", [])
        self.method = config.get("method", "POST").upper()
        self.headers = config.get("headers", {})
        self.retry_cfg = config.get("retry", {})
        self.ratelimit_cfg = config.get("ratelimit", {})
        self.auth_cfg = config.get("auth", {})

        self.auth_strategy = build_auth_strategy(self.auth_cfg)
        self.rate_limiter = create_rate_limiter(self.ratelimit_cfg)

        self.client = DynamicHttpClient(
            headers=self.headers,
            auth_strategy=self.auth_strategy,
            rate_limiter=self.rate_limiter,
            retry_count=self.retry_cfg.get("max_attempts", 3),
            retry_backoff_factor=self.retry_cfg.get("backoff_factor", 1.0),
            status_forcelist=self.retry_cfg.get("status_forcelist", [500, 502, 503, 504]),
        )

    async def update(self, data: dict):
        """Gửi data tới tất cả URLs."""
        print(f"[HttpTarget][{self.name}] Sending data to {len(self.urls)} URLs.")
        tasks = [self._send(url, data) for url in self.urls]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _create_file_payload(self, data: Any, file_name: str) -> dict:
        """Tạo payload dạng file nếu cần (placeholder)."""
        return {"file": (f"{file_name}.txt", data, "plain/text")}

    async def _send(self, url: str, data: Any, file_info: Any):
        try:
            file = self._create_file_payload(data, file_info.file_name)
            if file:
                response = await self.client.request_async(self.method, url, files=file)
            else:
                response = await self.client.request_async(self.method, url, data=data) 
            
            if response:
                print(f"[HttpTarget] Sent OK {url} ({response.status_code})")
            else:
                print(f"[HttpTarget] No response from {url}")
        except Exception as e:
            print(f"[HttpTarget] Failed to send to {url}: {e}")
