from re import A
from box import Box
from typing import Optional
from logspyq.api.proxy import LogseqProxy
from .utils import mkbox

class UI(LogseqProxy):

    # async def showMsg(self, content: str, status: str, key: Optional[str] = None, timeout: int = 3000):
    #     """showMsg(content: string, status?: string, opts?: Partial<UIMsgOptions>): Promise<string>"""
    #     return await self.emit("showMsg", content, status, **{"key": key, "timeout": timeout})
    
    # async def closeMsg(self, key: str):
    #     """closeMsg(key: string): void"""
    #     return await self.emit("closeMsg", key)
    
    pass