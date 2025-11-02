from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, List, Optional

class ObserverConfig(BaseModel):
    """Map nguồn → danh sách observer endpoint."""
    __root__: Dict[str, List[HttpUrl]] = Field(default_factory=dict)

    def get_endpoints(self, source: str) -> List[HttpUrl]:
        return self.__root__.get(source, [])

class DataSourceConfig(BaseModel):
    db_url: Optional[str] = None
    api_key: Optional[str] = None

class MessageQueueConfig(BaseModel):
    queue_url: str
    prefetch_count: int = 10
    retry: int = 3
