"""
device.py
18.11.2026

Manages a Tuya Device

Author:
Nilusink
"""
import tinytuya_async as tta


class TuyaDevice(tta.DeviceAsync):
    def __init__(
            self,
            dev_id: str,
            local_key: str,
            address: str | None = None,
            connection_timeout: int = 5,
            version: float = 3.4,
            persist: bool = True,
            **kwargs
    ) -> None:
        super().__init__(
            dev_id=dev_id,
            local_key=local_key,
            address=address,
            connection_timeout=connection_timeout,
            version=version,
            persist=persist,
            **kwargs
        )

        self._running = True
        self._bg_task_routine = None

    async def initialize(self) -> None:
        """
        send initial status request and start background task
        """
        self._bg_task_routine = self._bg_task()

    async def _bg_task(self) -> None:
        while self._running:
            data = await self.receive()
            print(f"received {data=}")
            await self.heartbeat()

    async def close(self, **kwargs) -> None:
        self._running = False
        await self._bg_task_routine
        await super().close(**kwargs)
