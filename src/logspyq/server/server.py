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
from async_signals.dispatcher import Signal
from box import Box, BoxList
from quart import Quart, render_template, request
from quart_cors import cors

from logspyq.server.plug import discover_agents

log = logging.getLogger(__name__)


class PluginServer:
    def __init__(
        self,
        log_level: int = logging.INFO,
        log_format: str = "%(levelname)s %(name)35s:%(lineno)03d - %(funcName)-20s - %(message)s",
        agent_name = "",
        agent = None,
    ):
        self._log_level = log_level
        self._log_format = log_format
        self._graph = {}
        self._db = None
        self._db_path = Path(click.get_app_dir("logspyq")) / "logspyq.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._scheduler = AsyncIOScheduler()
        self._sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self._quart_app = Quart(__name__)
        self._quart_app = cors(self._quart_app)
        self._app = socketio.ASGIApp(self._sio, self._quart_app)
        self._quart_app.route("/")(self._index)
        self._quart_app.route("/agent/")(self._agent_list)
        self._quart_app.route("/agent/<name>")(self._agent)
        self._quart_app.route("/agent/<name>/enable/toggle", methods=["POST"])(self._agent_enable_toggle)
        self._quart_app.route("/agent/<name>/setting", methods=["POST"])(self._agent_settings_update)
        self._sio.on("connect")(self._on_connect)
        self._sio.on("disconnect")(self._on_disconnect)
        self._sio.on("ready")(self._on_ready)
        self._sio.on("graph")(self._on_graph)
        self._sio.on("*")(self._on_any)
        self._signal_ready = Signal()
        if agent_name and agent:
            self._single_agent = True
            self._agents = {agent_name: agent}
        else:
            self._single_agent = False
            self._agents = {}


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

        log.info("Hi!")
        log.info(f"Starting server")
        try:
            log.info(f"Loading database from: {self._db_path}")
            self._db = dbm.open(str(self._db_path), "c")
            log.info("Starting scheduler")
            self._scheduler.start()
            asyncio.ensure_future(self._load_agents())
            log.info("Starting server")
            uvconfig = uvicorn.config.Config(
                self._app, host=host, port=port, debug=debug, reload=debug, log_level="info", log_config={
                    "version": 1,
                    "disable_existing_loggers": False,
                    "propagate": True,
                }
            )
            server = uvicorn.Server(uvconfig)
            await server.serve()
        except KeyboardInterrupt:
            log.info("Shutting down server")
        finally:
            log.info("Stopping scheduler")
            self._scheduler.shutdown()
            await asyncio.sleep(0.2)
            if self._db:
                log.info("Closing database")
                self._db.close()
                log.info("Database closed")
            log.info("Bye!")

    async def _load_agents(self):
        """
        Load agents.
        """
        assert self._db is not None
        if not self._agents:
            log.debug("Discovering agents")
            self._agents = discover_agents()
            for agent in self._agents.values():
                log.debug(f"Loading agent: {agent.name}")
                agent._set_server(self)
                await self._load_agent_settings_from_db(agent)
                enabled_key = f"agent:{agent.name}:enabled"
                if enabled_key in self._db:
                    enabled = self._db[enabled_key].decode("utf-8")
                    if enabled == "True":
                        log.info(f"  {agent.name} is enabled")
                        agent.enabled = True
                    else:
                        log.info(f"  {agent.name} is disabled")
                        agent.enabled = False
                else:
                    log.info(f"  {agent.name} is disabled by default")
                    agent.enabled = False
            log.info(f"Found {len(self._agents)} agents: {', '.join(self._agents.keys()) }")
        else:
            log.info("Skipping agent discovery")
            if self._single_agent:
                agent = list(self._agents.values())[0]
                log.warning(f"  {agent.name} is disabled, but single agent mode is enabled")
                agent.enabled = True

    
    async def _load_agent_settings_from_db(self, agent):
        """
        Load settings from database.
        """
        assert self._db is not None
        if agent.settings is None:
            log.debug(f"  {agent.name} has no settings")
            return
        log.debug(f"  {agent.name} has settings")
        for key, _value in agent.settings.__dataclass_fields__.items():
            db_key = f"agent:{agent.name}:setting:{key}"
            if db_key in self._db:
                setattr(agent.settings, key, self._db[db_key].decode("utf-8"))

    async def _register_agent_callbacks(self):
        for _name, agent in self._agents.items():
            await agent.register_callbacks_with_logseq()

    async def _on_connect(self, sid, _environ):
        """
        Handle client connect.
        """
        log.info(f"Logseq instance {sid!r} connected")

    async def _on_disconnect(self, sid):
        """
        Handle client disconnect.
        """
        log.info(f"Logseq instance {sid!r} disconnected")

    async def _on_ready(self, sid):
        """
        Called when a client is ready to receive data.
        """
        log.info(f"Logseq instance {sid!r} ready")
        await self._register_agent_callbacks()
        await self._signal_ready.send(sid)

    async def _on_graph(self, sid, data):
        """
        Handle graph event.
        """
        log.info(f"Logseq graph: {data!r}")
        self._graph = Box(data)

    async def _on_any(self, sid, event: str, *args):
        """
        Handle any event.
        """
        log.warning(f"*** Unhandled Event: {sid} {event} {args}")

    async def emit(self, name: str, *args, **data):
        """
        Emit an event to all connected clients.

        Args:
            name: The name of the event.
            *args: The arguments to pass to the event.
            **data: The data/opts to pass to the event.
        """
        data.update({"args": args})
        await self._sio.emit(name, data)
        log.debug(f"Sent event: {name} {data}")

    async def request(self, name: str, *args, timeout: int = 3, **data):
        """
        Emit an event and wait for reply from a client.

        Args:
            name: The name of the request.
            *args: The arguments to pass to the request.
            timeout: The timeout in seconds.
            **data: The data/opts to pass to the request.
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
            elif isinstance(response, str) and response == "null":
                return None
            else:
                return response
        except asyncio.TimeoutError:
            error_message = f"Request timed out: {name!r} {args!r}"
            log.error(error_message)
            raise TimeoutError(error_message)

    def on_cron(self, **kwargs):
        """
        Run a function on a cron schedule.
        """

        def outer(func):
            async def async_inner(*args):
                return await func(*args)

            kwargs.update({"trigger": "cron"})
            self._scheduler.add_job(async_inner, **kwargs)
            return async_inner

        return outer

    def on_interval(self, **kwargs):
        """
        Run a function at an interval.
        """

        def outer(func):
            async def _async_inner(*args):
                return await func(*args)

            kwargs.update({"trigger": "interval"})
            self._scheduler.add_job(_async_inner, **kwargs)
            return _async_inner

        return outer

    def on(self, event: str):
        """
        Decorator for handling socket.io events.
        """

        def outer(func):
            async def _async_inner(*args):
                return await func(*args)

            self._sio.on(event)(_async_inner)
            return _async_inner

        return outer
    
    def on_ready(self):
        """
        Decorator for handling ready event.
        """

        def outer(func):
            async def _async_inner(*args):
                return await func(*args)

            self._signal_ready.connect(_async_inner)
            return _async_inner

        return outer
        

    async def _index(self):
        """
        Render the index page.
        """
        return await render_template("index.html", agent_list=self._agents)
    
    async def _agent(self, name):
        """
        Render the agent page.
        """
        agent = self._agents.get(name)
        return await render_template("agent.html", agent=agent)

    async def _agent_list(self):
        """
        Return a list of agents.
        """
        return await render_template("index.html", agent_list=self._agents)

    async def _agent_enable_toggle(self, name):
        """
        Toggle an agent's enabled state.
        """
        assert self._db is not None
        agent = self._agents.get(name)
        if agent:
            agent.enabled = not agent.enabled
            self._db[f"agent:{name}:enabled"] = str(agent.enabled)
            if agent.enabled:
                await agent.register_callbacks_with_logseq(fire_ready_now=True)
            return await render_template("_include/agent_list_item_status.html", agent=agent)
        else:
            return "Agent not found", 404
        
    async def _agent_settings_update(self, name):
        """
        Update an agent's setting.
        """
        assert self._db is not None
        agent = self._agents.get(name)
        if agent:
            data = await request.form 
            if data:
                for key, value in data.items():
                    self._db[f"agent:{name}:setting:{key}"] = value
                await self._load_agent_settings_from_db(agent)
                return "OK"
            else:
                return "No data", 400
        else:
            return "Agent not found", 404