from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal

class AuthConfig(BaseModel):
    strategy: Literal["bearer", "api_key", "basic", "no_auth"] = "no_auth"
    key: Optional[str] = None
    value: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    in_: Optional[Literal["header", "query"]] = Field(default="header", alias="in")


class RetryConfig(BaseModel):
    max_attempts: int = 3
    backoff_factor: float = 1.0
    status_forcelist: List[int] = Field(default_factory=lambda: [500, 502, 503, 504])


class RateLimitConfig(BaseModel):
    strategy: Literal["response", "header", "fixed"] = "response"
    json_fields: Dict[str, List[str]] = Field(default_factory=dict)
    default_wait: float = 0.3
    max_wait: float = 30.0
