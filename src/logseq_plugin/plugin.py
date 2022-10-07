import asyncio
from dataclasses import asdict
from pathlib import Path
from typing import Union

import socketio
import uvicorn

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from box import Box
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


from .app import LogseqApp
from .db import LogseqDB
from .editor import LogseqEditor
from .utils import mkbox


class LogseqPlugin(object):
    def __init__(
        self, settings: Union[object, None] = None, assets_path: str = "assets"
    ):
        self._port = 8484
        self._host = "127.0.0.1"
        self._handlers = {}
        self.settings = settings
        self.assets_path = Path(assets_path)
        self.assets_path.mkdir(exist_ok=True)
        self.routes = [
            Mount("/assets", app=StaticFiles(directory="assets"), name="assets")
        ]
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self.emit = self.sio.emit
        self.starlette_app = Starlette(debug=True, routes=self.routes)
        self.asgi_app = socketio.ASGIApp(self.sio, self.starlette_app)
        self.sio.on("connect", self._on_connect)
        self.sio.on("disconnect", self._on_disconnect)
        self.sio.on("plugin_loaded", self._on_plugin_loaded)
        self.Editor = LogseqEditor(self)
        self.App = LogseqApp(self)
        self.DB = LogseqDB(self)

    def run(self, port: int, host: str = "127.0.0.1"):
        asyncio.run(self._run(port=port, host=host))

    async def _run(self, port: int, host: str = "127.0.0.1"):
        self._port = int(port)
        self._host = str(host)
        await asyncio.wait(
            [
                asyncio.create_task(self._start_uvicorn()),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

    async def _start_uvicorn(self):
        uvconfig = uvicorn.config.Config(
            self.asgi_app, host="localhost", port=int(8484)
        )
        server = uvicorn.server.Server(uvconfig)
        await server.serve()

    async def _load_settings(self):
        if self.settings:
            schema = self.settings.schema()  # type: ignore
            try:
                settings = await self.request(
                    "logseq.useSettingsSchema", schema, timeout=3
                )
                valid_keys = asdict(self.settings).keys()
                for key, value in settings.items():  # type: ignore
                    if key in valid_keys:
                        setattr(self.settings, key, value)
            except TimeoutError as e:
                print(f"Logseq plugin settings: error sending setting_schema: {e}")

    async def _run_handlers(self, event_name, *args):
        if self._handlers.get(event_name):
            plugin_ready_handler = self._handlers.get(event_name)
            if plugin_ready_handler:
                asyncio.create_task(plugin_ready_handler(*args))

    async def _on_connect(self, sid, _environ, _):
        print(f"Logseq plugin connected: {sid}")

    async def _on_disconnect(self, sid):
        print(f"Logseq plugin disconnected: {sid}")

    async def _on_plugin_loaded(self, _sid):
        await self._load_settings()
        await self.Editor._register_handlers()
        await self._run_handlers("plugin_ready")

    async def request(self, name, *args, timeout: float = 10):
        response = None

        async def set_response(r):
            nonlocal response
            response = r

        async def wait_loop():
            while not response:
                await asyncio.sleep(0.01)
            return response

        await self.emit(name, (*args,), callback=set_response)
        try:
            await asyncio.wait_for(wait_loop(), timeout=timeout)
            return mkbox(response)
        except asyncio.exceptions.TimeoutError:
            raise TimeoutError(f"Request {name!r} timed out")

    def on(self, event_name):
        def outer(func):
            async def async_inner(_sid, *args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self._handlers.update({event_name: async_inner})
            return async_inner

        return outer

    def on_plugin_ready(self):
        def decorator(func):
            self._handlers.update({"plugin_ready": func})
            return func

        return decorator

    def on_http_post(self, path: str):
        def decorator(func):
            self.starlette_app.add_route(path, func, methods=["POST"])
            return func

        return decorator
