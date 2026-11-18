"""
wserver.py
18.11.2026

FastAPI webserver to make devices accessible through Tuya

Author:
Nilusink
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# import icecream as ic
import uvicorn

from device_manager import DeviceManager
# from device import TuyaDevice


class DeviceSetRequest(BaseModel):
    dps: int
    value: bool | int | float


class HTTPServer:
    def __init__(
            self,
            ip: str,
            port: int,
            device_manager: DeviceManager,
    ) -> None:
        self._ip = ip
        self._port = port
        self._manager = device_manager

        self._app = FastAPI()

        # register endpoints
        self._setup_routes()

    def _setup_routes(self) -> None:
        # is alive
        @self._app.get("/")
        async def index() -> dict:
            """is alive check"""
            return {"status": "success"}

        @self._app.get("/device/{device_id}")
        async def device_status(device_id: str) -> dict:
            if device_id not in self._manager:
                raise HTTPException(status_code=404, detail="Device not found")

            await self._manager[device_id].status()
            dev_answer = await self._manager[device_id].receive()

            return {"status": "success", "data": dev_answer}

        @self._app.get("/devices")
        async def device_list() -> dict:
            return {"status": "success", "data": self._manager.get_ids()}

        @self._app.post("/device/{device_id}")
        async def device_set(device_id: str, data: DeviceSetRequest) -> dict:
            if device_id not in self._manager:
                raise HTTPException(status_code=404, detail="Device not found")

            await self._manager[device_id].set_value(
                data.dps,
                data.value
            )
            dev_answer = await self._manager[device_id].receive()

            return {"status": "success", "data": dev_answer}

        @self._app.post("/device/{device_id}/toggle")
        async def device_toggle(device_id: str) -> dict:
            if device_id not in self._manager:
                raise HTTPException(status_code=404, detail="Device not found")

            await self._manager[device_id].toggle()
            dev_answer = await self._manager[device_id].receive()

            return {"status": "success", "data": dev_answer}

    async def serve(self):
        """Run this buffer as its own FastAPI server."""
        config = uvicorn.Config(
            self._app,
            host=self._ip,
            port=self._port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()