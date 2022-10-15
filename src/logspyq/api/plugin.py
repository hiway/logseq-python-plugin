import logging
from logspyq.api.editor import Editor
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
        log.debug("Initializing LSPluginUser")
        # Attach to or start a plugin server
        if server:
            log.info("Using provided PluginServer")
            self._set_server(server)
        else:
            log.warning("No server provided, creating a new one")
            self._set_server(PluginServer(log_level=log_level, log_format=log_format, agent=self, agent_name="LSPluginUser"))
        # Add proxies
        self.Editor = Editor(self, "Editor")
        log.debug("Initialized LSPluginUser")

    def _set_server(self, server):
        self._server = server
        self.emit = self._server.emit
        self.request = self._server.request
        self.on = self._server._sio.on
        self.on_cron = self._server.on_cron
        self.on_interval = self._server.on_interval
        self.run = self._server.run

    async def register_callbacks_with_logseq(self):
        log.debug("Register callbacks with Logseq")
        await self.Editor.register_callbacks_with_logseq()
