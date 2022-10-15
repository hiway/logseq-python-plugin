from re import A
from box import Box
from typing import Optional
from logspyq.api.proxy import LogseqProxy
from .utils import mkbox

class Assets(LogseqProxy):
    async def listFilesOfCurrentGraph(self, exts: str):
        return await self.request("listFilesOfCurrentGraph", exts)
        
        
    
