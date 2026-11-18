"""
main.py
18.11.2026

Makes Tuya devices accessible through HTTP requests.

Author:
Nilusink
"""
from contextlib import suppress
from icecream import ic
import asyncio

from device_manager import DeviceManager
from wserver import HTTPServer


async def main() -> None:
    dev_man = DeviceManager("./devices.json")
    await dev_man.initialize()

    wserver = HTTPServer("0.0.0.0", 12344, dev_man)
    ic("initialized, serving")

    with suppress(Exception):
        await wserver.serve()

    ic("closing")

    # close device manager
    await dev_man.close()


if __name__ == "__main__":
    asyncio.run(main())