from re import A
from box import Box
from typing import Optional
from logspyq.api.proxy import LogseqProxy
from .utils import mkbox

class Git(LogseqProxy):
    async def execCommand(self, *args):
        return await self.request("execCommand", args)

    async def loadIgnoreFile(self):
        return await self.emit("loadIgnoreFile")

    async def saveIgnoreFile(self, content: str):
        return await self.emit("saveIgnoreFile", content)
