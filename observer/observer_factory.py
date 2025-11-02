from observer.http_target import HttpTarget
from observer.rabbitmq_target import RabbitMQTarget
from observer.base_observer import BaseObserver

def create_observer(config: dict) -> BaseObserver | None:
    """Tạo target phù hợp theo type."""
    ttype = config.get("type", "").lower()
    if ttype == "http":
        return HttpTarget(config)
    elif ttype == "rabbitmq":
        return RabbitMQTarget(config)
    else:
        print(f"[ObserverManager] Unknown target type: {ttype}")
        return None