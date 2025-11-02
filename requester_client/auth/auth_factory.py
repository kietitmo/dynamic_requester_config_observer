from .strategies import (
    BearerAuthStrategy,
    ApiKeyAuthStrategy,
    BasicAuthStrategy,
    NoAuthStrategy,
)

def build_auth_strategy(config: dict | None):
    if not config:
        return NoAuthStrategy()

    strategy = config.get("strategy", "none").lower()

    match strategy:
        case "bearer":
            return BearerAuthStrategy(token=config.get("token", ""))
        case "api_key":
            return ApiKeyAuthStrategy(
                header_name=config.get("key", "x-api-key"),
                key=config.get("value", ""),
            )
        case "basic":
            return BasicAuthStrategy(
                username=config.get("username", ""),
                password=config.get("password", ""),
            )
        case _:
            return NoAuthStrategy()