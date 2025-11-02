import asyncio
import time
import httpx
from requester_client.rate_limiter.base_rate_limiter import BaseRateLimiter


class HeaderRateLimiter(BaseRateLimiter):
    """
    RateLimiter linh hoạt đọc header tùy config:
    - Cho phép định nghĩa danh sách header động cho Retry-After, Reset, Limit.
    - Có fallback default_wait nếu không tìm thấy.
    """

    def __init__(self, config: dict | None = None):
        super().__init__()
        cfg = config or {}

        headers = cfg.get("headers", {})
        self.retry_keys = [k.lower() for k in headers.get("retry_after", ["retry-after"])]
        self.reset_keys = [k.lower() for k in headers.get("reset", ["x-ratelimit-reset", "ratelimit-reset"])]
        self.limit_keys = [k.lower() for k in headers.get("limit", [])]

        self.default_wait = cfg.get("default_wait", 0.5)
        self.max_wait = cfg.get("max_wait", 60)

    async def handle_rate_limit(self, response: httpx.Response):
        """Main entry: handle rate-limit based on configured headers."""
        wait_time = self._determine_wait_time(response.headers)
        await self._sleep(wait_time)

    def _determine_wait_time(self, headers: dict) -> float:
        """Tính toán thời gian chờ dựa trên các header có thể có."""
        now = time.time()

        wait_time = (
            self._extract_retry_after(headers)
            or self._extract_reset_timestamp(headers, now)
            or self._extract_from_limit(headers)
            or self.default_wait
        )

        return min(wait_time, self.max_wait)

    def _extract_retry_after(self, headers: dict) -> float | None:
        """Đọc Retry-After headers."""
        for key in self.retry_keys:
            if key in headers:
                try:
                    return float(headers[key])
                except ValueError:
                    continue
        return None

    def _extract_reset_timestamp(self, headers: dict, now: float) -> float | None:
        """Đọc RateLimit-Reset headers (timestamp)."""
        for key in self.reset_keys:
            if key in headers:
                try:
                    reset_ts = float(headers[key])
                    return max(0, reset_ts - now)
                except ValueError:
                    continue
        return None

    def _extract_from_limit(self, headers: dict) -> float | None:
        """Tự động suy ra thời gian chờ dựa vào limit headers (nếu có)."""
        for key in self.limit_keys:
            if key in headers:
                try:
                    rate = float(headers[key])
                    if rate > 0:
                        return 1 / rate
                except ValueError:
                    continue
        return None

    async def _sleep(self, wait_time: float):
        """Sleep và log ra console."""
        print(f"[RateLimit] Waiting {wait_time:.2f}s (dynamic header policy)...")
        await asyncio.sleep(wait_time)
