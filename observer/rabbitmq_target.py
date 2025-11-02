import asyncio
from observer.base_observer import BaseObserver

class RabbitMQTarget(BaseObserver):
    """Demo đơn giản cho target RabbitMQ."""

    def __init__(self, config: dict):
        super().__init__(name=config.get("name", "rabbitmq_target"), config=config)
        self.topic = config.get("topic", "")
        self.connection = None  # giả sử có aio-pika ở đây

    async def update(self, data: dict):
        """Giả lập gửi message lên topic."""
        await asyncio.sleep(0.1)
        print(f"[RabbitMQTarget] Published to topic '{self.topic}' -> {data}")
