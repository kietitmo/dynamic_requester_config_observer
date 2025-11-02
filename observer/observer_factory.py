from observer.targets.http_target import HttpTarget
from observer.targets.rabbitmq_target import RabbitMQTarget
from observer.targets.base_observer import BaseObserver

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