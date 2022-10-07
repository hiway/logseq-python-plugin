class LogseqApp(object):
    def __init__(self, plugin):
        self._plugin = plugin

    async def showMsg(self, message: str, type: str = "success"):
        await self._plugin.emit("logseq.App.showMsg", (message, type))
