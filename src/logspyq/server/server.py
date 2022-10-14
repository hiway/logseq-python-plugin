"""
Socket.IO server for logspyq plugins.
"""
import asyncio
import dbm
import logging

from pathlib import Path

import click
import socketio
import uvicorn
import uvloop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from box import Box, BoxList
from quart import Quart, render_template
from quart_cors import cors


from logspyq.server.logger import log


class PluginServer:
    def __init__(
        self,
        log_level: int = logging.INFO,
        log_format: str = "%(asctime)-15s %(levelname)-8s %(message)s",
    ):
        self._log_level = log_level
        self._log_format = log_format
        self._db = None
        self._db_path = Path(click.get_app_dir("logspyq")) / "logspyq.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._scheduler = AsyncIOScheduler()
        self._sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self._quart_app = Quart(__name__)
        self._quart_app = cors(self._quart_app)
        self._app = socketio.ASGIApp(self._sio, self._quart_app)
        self._quart_app.route("/")(self._index)
        self._sio.on("connect")(self._on_connect)
        self._sio.on("disconnect")(self._on_disconnect)
        self._sio.on("ready")(self._on_ready)

    def run(self, host: str, port: int, debug: bool = False):
        """
        Run the server.
        """
        asyncio.run(self._run(host=host, port=port, debug=debug))

    async def _run(self, host: str, port: int, debug: bool):
        """
        Run the server, async.
        """
        uvloop.install()
        if debug:
            logging.basicConfig(level=logging.DEBUG, format=self._log_format)
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(self._log_level)
            logging.basicConfig(level=self._log_level, format=self._log_format)
        log.propagate = False
        formatter = logging.Formatter(self._log_format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        log.addHandler(handler)

        log.info(f"Starting server")
        try:
            log.info(f"Loading database from: {self._db_path}")
            self._db = dbm.open(str(self._db_path), "c")
            log.info("Starting scheduler")
            self._scheduler.start()
            log.info("Starting server")
            uvconfig = uvicorn.config.Config(
                self._app, host=host, port=port, debug=debug
            )
            server = uvicorn.Server(uvconfig)
            await server.serve()
        except KeyboardInterrupt:
            log.info("Shutting down server")
        finally:
            log.info("Stopping scheduler")
            self._scheduler.shutdown()
            if self._db:
                log.info("Closing database")
                self._db.close()

    async def _index(self):
        """
        Render the index page.
        """
        return await render_template("index.html")

    async def _on_connect(self, sid, _environ):
        """
        Handle client connect.
        """
        log.info(f"Client {sid} connected")

    async def _on_disconnect(self, sid):
        """
        Handle client disconnect.
        """
        log.info(f"Client {sid} disconnected")

    async def _on_ready(self, sid):
        """
        Called when a client is ready to receive data.
        """
        log.info(f"Client {sid} ready")

    async def emit(self, name: str, *args, **data):
        """
        Emit an event to all connected clients.

        Args:
            name: The name of the event.
            *args: The arguments to pass to the event.
            **data: The data to pass to the event.
        """
        data.update({"args": args})
        await self._sio.emit(name, data)

    async def request(self, name: str, *args, timeout: int = 3, **data):
        """
        Emit an event and wait for reply from a client.

        Args:
            name: The name of the request.
            *args: The arguments to pass to the request.
            timeout: The timeout in seconds.
            **data: The data to pass to the request.
        """
        response = None

        async def set_response(r):
            nonlocal response
            response = r

        async def wait_loop():
            while not response:
                await asyncio.sleep(0.001)
            return response

        log.debug(f"Request: {name!r} <== {args!r}")
        data.update({"args": args})
        await self._sio.emit(name, data, callback=set_response)
        try:
            await asyncio.wait_for(wait_loop(), timeout=timeout)
            log.debug(f"Response: {response!r}")
            if isinstance(response, dict):
                return Box(response)
            elif isinstance(response, list):
                return BoxList(response)
            else:
                return response
        except asyncio.TimeoutError:
            error_message = f"Request timed out: {name!r} {args!r}"
            log.error(error_message)
            raise TimeoutError(error_message)
