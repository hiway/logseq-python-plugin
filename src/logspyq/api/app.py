from re import A
from box import Box
from typing import Optional, List
from logspyq.api.proxy import LogseqProxy
from .utils import mkbox

class App(LogseqProxy):
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

    def onCurrentGraphChanged(self):
        def decorator(func):
            event_name = f"current-graph-changed"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onCurrentGraphChanged",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator
    
    def onMacroRendererSlotted(self):
        def decorator(func):
            event_name = f"macro-render-slotted"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onMacroRendererSlotted",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator

    def onPageHeadActionsSlotted(self):
        def decorator(func):
            event_name = f"page-head-actions-slotted"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onPageHeadActionsSlotted",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator
    
    def onRouteChanged(self):
        def decorator(func):
            event_name = f"route-changed"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onRouteChanged",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator
    
    def onSidebarVisibleChanged(self):
        def decorator(func):
            event_name = f"sidebar-visible-changed"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onSidebarVisibleChanged",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator

    def onThemeModeChanged(self):
        def decorator(func):
            event_name = f"theme-mode-changed"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onThemeModeChanged",
                event_name=event_name,
                func=_async_inner,
            )
            return _async_inner

        return decorator

    async def execGitCommand(self, *args):
        return await self.request("execGitCommand", args)

    async def showMsg(self, content: str, status: str, key: Optional[str] = None, timeout: int = 3000):
        """showMsg(content: string, status?: string, opts?: Partial<UIMsgOptions>): Promise<string>"""
        return await self.emit("showMsg", content, status, **{"key": key, "timeout": timeout})
        
