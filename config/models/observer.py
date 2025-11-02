from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, List, Optional, Union, Literal, Any
from .common import AuthConfig, RetryConfig, RateLimitConfig


class HttpTargetConfig(BaseModel):
    name: str
    type: Literal["http"]
    method: str = "POST"
    urls: List[HttpUrl]
    headers: Dict[str, str] = Field(default_factory=dict)
    params: Optional[Dict[str, Any]] = None
    auth: Optional[AuthConfig] = None
    retry: Optional[RetryConfig] = None
    ratelimit: Optional[RateLimitConfig] = None


class RabbitMQTargetConfig(BaseModel):
    name: str
    type: Literal["rabbitmq"]
    topic: str


TargetConfig = Union[HttpTargetConfig, RabbitMQTargetConfig]


class SourceObserverConfig(BaseModel):
    targets: List[TargetConfig]


class ObserverConfig(BaseModel):
    """Map source → danh sách targets."""
    __root__: Dict[str, SourceObserverConfig]

    def get_targets(self, source: str) -> List[TargetConfig]:
        return self.__root__.get(source, SourceObserverConfig(targets=[])).targets
