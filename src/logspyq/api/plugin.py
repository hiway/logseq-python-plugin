import logging
from logspyq.api.app import App
from logspyq.api.editor import Editor
from logspyq.api.ui import UI
from logspyq.server.logger import log
from logspyq.server.server import PluginServer


class LSPluginUser:
    def __init__(
        self,
        server=None,
        log_level=logging.INFO,
        log_format="%(asctime)-15s %(levelname)-8s %(message)s",
    ) -> None:
        self._register_callbacks = {
            # "Editor.registerSlashCommand", "slash-command-COMMAND-NAME"
        }
        self._log_level = log_level
        self._log_format = log_format
        log.debug("Initializing LSPluginUser")
        self._server = server
        # Add proxies
        self.App = App(self, "App")
        self.Editor = Editor(self, "Editor")
        self.UI = UI(self, "UI")
        self.log = log
        self._schedules = {}
        self._events = {}
        log.debug("Initialized LSPluginUser")

    def _set_server(self, server):
        self._server = server
        self.emit = self._server.emit
        self.request = self._server.request

    async def register_callbacks_with_logseq(self):
        log.debug("Register callbacks with Logseq")

        await self.App.register_callbacks_with_logseq()
        await self.Editor.register_callbacks_with_logseq()
        await self.UI.register_callbacks_with_logseq()
        assert self._server
        for func, kwargs in self._schedules.items():
            self._server._scheduler.add_job(func, **kwargs)
        for func, event in self._events.items():
            self._server._sio.on(event)(func)

    def on_cron(self, **kwargs):
        """
        Run a function on a cron schedule.
        """

        def outer(func):
            async def async_inner(*args):
                return await func(*args)

            kwargs.update({"trigger": "cron"})
            self._schedules.update({async_inner: kwargs})
            return async_inner

        return outer

    def on_interval(self, **kwargs):
        """
        Run a function at an interval.
        """

        def outer(func):
            async def async_inner(*args):
                return await func(*args)

            kwargs.update({"trigger": "interval"})
            self._schedules.update({async_inner: kwargs})
            return async_inner

        return outer

    def on(self, event: str):
        """
        Decorator for handling socket.io events.
        """

        def outer(func):
            async def async_inner(*args):
                if len(args) == 1 and args[0] == "null":
                    return await func(None)
                else:
                    return await func(*args)

            self._events.update({async_inner: event})
            return async_inner

        return outer

    def run(self, host="localhost", port=0, debug=False):
        # Attach to or start a plugin server
        if self._server:
            log.info("Using provided PluginServer")
            self._set_server(self._server)
        else:
            log.warning("No server provided, creating a new one")
            self._set_server(
                PluginServer(
                    log_level=self._log_level,
                    log_format=self._log_format,
                    agent=self,
                    agent_name="LSPluginUser",
                )
            )
        assert self._server
        self._server.run(host=host, port=port, debug=debug)

    async def provideUI(self, key, slot, template):
        await self.emit("provideUI", {"key": key, "slot": slot, "template": template})