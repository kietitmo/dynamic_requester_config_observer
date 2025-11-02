import asyncio
from config.settings import settings
from observer.observer_factory import create_observer

class ObserverManager:
    """Singleton quản lý toàn bộ observer (mỗi source có nhiều target)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_observers()
        return cls._instance

    def _init_observers(self):
        """Khởi tạo tất cả observer từ settings."""
        self.observers = {}
        observer_cfg = settings.observer or {}

        for source, cfg in observer_cfg.items():
            targets_cfg = cfg.get("targets", [])
            targets = [create_observer(tcfg) for tcfg in targets_cfg]
            self.observers[source] = targets

        print(f"[ObserverManager] Initialized {len(self.observers)} observers.")


    async def handle_message(self, source: str, data: dict):
        """Gửi message tới các target tương ứng với source."""
        targets = self.observers.get(source)
        if not targets:
            print(f"[ObserverManager] No targets for source '{source}'")
            return

        tasks = [t.update(data) for t in targets if t]
        await asyncio.gather(*tasks, return_exceptions=True)
