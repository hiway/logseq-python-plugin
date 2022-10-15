from re import A
from box import Box
from typing import Optional, List
from logspyq.api.proxy import LogseqProxy
from .utils import mkbox

class DB(LogseqProxy):
    async def datascriptQuery(self, query: str, inputs: List[str]):
        return await self.request("datascriptQuery", query, inputs)

    async def q(self, dsl: str):
        return await self.request("q", dsl)
    
    def onBlockRendererSlotted(self):
        def decorator(func):
            event_name = f"block-render-slotted"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onBlockRendererSlotted",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator
    
    def onChanged(self):
        def decorator(func):
            event_name = f"changed"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onChanged",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator
    
    def onBlockChanged(self, uuid: str):
        def decorator(func):
            event_name = f"block-changed-{uuid}"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onBlockChanged",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator
    
