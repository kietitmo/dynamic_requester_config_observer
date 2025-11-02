from requester_client.rate_limiter.header_rate_limiter import HeaderRateLimiter
from requester_client.rate_limiter.response_rate_limiter import ResponseRateLimiter
from requester_client.rate_limiter.base_rate_limiter import BaseRateLimiter

def create_rate_limiter(config: dict | None) -> BaseRateLimiter | None:
    if not config:
        return None

    strategy = config.get("strategy", "header").lower()

    if strategy == "header":
        return HeaderRateLimiter(config)
    elif strategy == "response":
        return ResponseRateLimiter(config)
    else:
        print(f"[WARN] Unknown rate-limit strategy: {strategy}")
        return None