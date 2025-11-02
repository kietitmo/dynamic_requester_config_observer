import asyncio
import signal
import sys
import logging

from config.settings import settings
from observer.observer_manager import ObserverManager
from queue.message_queue import MockMessageQueue  # hoặc real MQ consumer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger("main")


async def message_consumer_loop():
    """
    Vòng lặp chính nhận message từ queue và xử lý qua observer manager.
    """
    observer_mgr = ObserverManager()
    queue = MockMessageQueue()

    logger.info("[Main] Starting message consumption loop...")

    async for message in queue.consume():
        source = message.get("source")
        data = message.get("data")
        logger.info(f"[Main] Received message from source: {source}")
        await observer_mgr.handle_message(source, data)


async def main():
    """
    Entry point: khởi tạo app, handle signal, run consumer.
    """
    logger.info(f"[Startup] Environment: {settings.environment.upper()} | Debug: {settings.debug}")

    stop_event = asyncio.Event()

    def _signal_handler(sig, frame):
        logger.warning(f"[Main] Received signal {sig.name}, shutting down...")
        stop_event.set()

    # Đăng ký graceful shutdown
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Chạy consumer loop song song với wait stop_event
    task = asyncio.create_task(message_consumer_loop())

    await stop_event.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("[Main] Message loop stopped gracefully.")

    logger.info("[Main] Application exited cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("[Main] Interrupted by user.")
        sys.exit(0)
