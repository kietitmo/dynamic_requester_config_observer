from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional, Literal, Any
from .common import AuthConfig, RetryConfig


class DataSourceItem(BaseModel):
    type: Literal["http", "db", "s3"]
    base_url: Optional[HttpUrl] = None
    endpoints: Optional[str] = None
    auth: Optional[AuthConfig] = None
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    retry: Optional[RetryConfig] = None


class DataSourceConfig(BaseModel):
    __root__: Dict[str, DataSourceItem]

    def get(self, name: str) -> Optional[DataSourceItem]:
        return self.__root__.get(name)
