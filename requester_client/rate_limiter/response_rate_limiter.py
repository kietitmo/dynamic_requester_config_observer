import asyncio
import time
import httpx
from requester_client.rate_limiter.base_rate_limiter import BaseRateLimiter
from requester_client.utils.json_helper import get_nested_key


class ResponseRateLimiter(BaseRateLimiter):
    """
    RateLimiter đọc thông tin rate-limit từ response JSON.
    - Hỗ trợ dynamic key paths (vd: "data.rate_limit.reset").
    - Có fallback default_wait.
    """

    def __init__(self, config: dict | None = None):
        super().__init__()
        cfg = config or {}

        fields = cfg.get("json_fields", {})
        self.retry_keys = fields.get("retry_after", ["retry_after"])
        self.reset_keys = fields.get("reset", ["rate_limit_reset"])

        self.default_wait = cfg.get("default_wait", 0.5)
        self.max_wait = cfg.get("max_wait", 60)

    async def handle_rate_limit(self, response: httpx.Response):
        wait_time = self._determine_wait_time(response)
        await self._sleep(wait_time)

    def _determine_wait_time(self, response: httpx.Response) -> float:
        data = self._parse_json(response)
        now = time.time()

        wait_time = (
            self._extract_retry_after(data)
            or self._extract_reset_timestamp(data, now)
            or self.default_wait
        )

        return min(wait_time, self.max_wait)

    def _parse_json(self, response: httpx.Response) -> dict:
        try:
            return response.json()
        except Exception:
            return {}

    def _extract_retry_after(self, data: dict) -> float | None:
        for path in self.retry_keys:
            val = get_nested_key(data, path)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    continue
        return None

    def _extract_reset_timestamp(self, data: dict, now: float) -> float | None:
        for path in self.reset_keys:
            val = get_nested_key(data, path)
            if val is not None:
                try:
                    reset_ts = float(val)
                    return max(0, reset_ts - now)
                except (ValueError, TypeError):
                    continue
        return None

    async def _sleep(self, wait_time: float):
        print(f"[RateLimit] Waiting {wait_time:.2f}s (response JSON policy)...")
        await asyncio.sleep(wait_time)
