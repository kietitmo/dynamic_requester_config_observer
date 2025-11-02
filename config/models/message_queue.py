from pydantic import BaseModel
from typing import Dict, Optional, Literal, Any


class SSLConfig(BaseModel):
    ca_certs: Optional[str] = None


class MessageQueueConfig(BaseModel):
    type: Literal["rabbitmq", "kafka"] = "rabbitmq"
    host: str
    port: int = 5672
    username: str
    password: str
    virtual_host: str = "/"
    connection_params: Dict[str, Any] = {}
    exchange: str
    exchange_type: str = "direct"
    durable: bool = True
    auto_delete: bool = False
    delivery_mode: int = 2
    ssl: bool = False
    ssl_options: Optional[SSLConfig] = None
