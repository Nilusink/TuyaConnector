"""
device_manager.py
18.11.2026

Dynamically manages all tuya devices.

Author:
Nilusink
"""
from types import EllipsisType
import json
import os

from device import TuyaDevice


class DeviceManager:
    """
    :cvar _instance: singular DeviceManager instance

    :ivar _file_path: device settings file path
    :ivar _devices: dict of device_id: device
    """

    _instance: DeviceManager | EllipsisType = ...

    # only allow one instance
    def __new__(cls, *args, **kwargs):
        if cls._instance is ...:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self._devices: dict[str, TuyaDevice] = {}

    async def initialize(self) -> None:
        """set up the device manager"""
        await self._load_devices(self._file_path)

    async def _load_devices(self, path: str) -> None:
        """
        Load devices from a specified path.

        :param path: file path
        :raises FileNotFoundError: if invalid path
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Invalid path: {path=}")

        with open(path, "r") as f:
            for device in json.load(f):
                await self._add_device(**device)

    async def _add_device(self, dev_id: str, local_key: str, **kwargs) -> None:
        """
        Add a single device to device_manager

        :param dev_id: tuya device id
        :param local_key: tuya device local key
        :param kwargs: optional args
        """
        # skip already existing devices
        if dev_id in self._devices:
            return

        self._devices[dev_id] = TuyaDevice(dev_id, local_key, **kwargs)
        await self._devices[dev_id].initialize()

    def get_ids(self) -> list[str]:
        """
        :return: a list of all device ids
        """
        return list(self._devices.keys())

    async def close(self) -> None:
        """Disconnect all devices"""
        for device in self._devices.values():
            await device.close()

    def get_device(self, dev_id: str) -> TuyaDevice:
        return self._devices[dev_id]

    def __getitem__(self, dev_id: str) -> TuyaDevice:
        return self._devices[dev_id]

    def __contains__(self, dev_id: str) -> bool:
        return dev_id in self._devices
