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

    def registerCommand(
        self,
        type,
        *,
        desc: Optional[str] = None,
        key: Optional[str] = None,
        keybinding: Optional[dict] = None,
        label: Optional[str] = None,
        palette: bool = False,
    ):
        def decorator(func):
            event_name = f"command-{key}"
            # Gather all opts
            opts = {
                "desc": desc,
                "key": key,
                "keybinding": keybinding,
                "label": label,
                "palette": palette,
            }

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "registerCommand",
                event_name=event_name,
                type=type,
                opts=opts,
                func=_async_inner,
            )
            return _async_inner

        return decorator

    def registerCommandPalette(self, key: str, binding: str, label: str, mac: Optional[str]=None, mode: Optional[str]=None):
        """registerCommandPalette(opts: { key: string; keybinding?: SimpleCommandKeybinding; label: string }, action: SimpleCommandCallback): void"""
        def decorator(func):
            event_name = f"command-{key}"
            keybinding = {"mac": mac, "mode": mode, "binding": binding}


            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "registerCommand",
                event_name=event_name,
                key=key,
                keybinding=keybinding,
                label=label,
                func=_async_inner,
            )
            return _async_inner

        return decorator
        
    def registerCommandShortcut(self, keybinding: dict):
        """registerCommandShortcut(keybinding: SimpleCommandKeybinding, action: SimpleCommandCallback): void"""
        def decorator(func):
            event_name = f"command-{keybinding['binding']}"
            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "registerCommandShortcut",
                event_name=event_name,
                keybinding=keybinding,
                func=_async_inner,
            )
            return _async_inner

        return decorator
    
    def registerPageMenuItem(self, tag: str):
        """registerPageMenuItem(tag: string, action: (e: IHookEvent & { page: string }) => void): void"""
        def decorator(func):
            event_name = f"page-menu-item-{tag}"
            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "registerPageMenuItem",
                event_name=event_name,
                tag=tag,
                func=_async_inner,
            )
            return _async_inner

        return decorator

    def registerUIItem(self, type: str, key: str, template: str):
        """registerUIItem(type: string, key: string, template: string): void"""
        def decorator(func):
            event_name = f"ui-item-{key}"
            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "registerUIItem",
                event_name=event_name,
                type=type,
                opts={"key": key, "template": template},
                func=_async_inner,
            )
            return _async_inner

        return decorator

    async def execGitCommand(self, *args):
        return await self.request("execGitCommand", args)

    async def getCurrentGraph(self):
        return await self.request("getCurrentGraph")

    async def getInfo(self):
        return await self.request("getInfo")

    async def getStateFromStore(self, path: str):
        return await self.request("getStateFromStore", path)

    async def getUserConfigs(self):
        return await self.request("getUserConfigs")

    async def getUserInfo(self):
        return await self.request("getUserInfo")

    async def invokeExternalCommand(self, type: str, *args):
        return await self.request("invokeExternalCommand", type, args)

    async def openExternalLink(self, url: str):
        return await self.request("openExternalLink", url)

    async def pushState(self, k: str, params: Optional[str], query: Optional[str]):
        return await self.request("pushState", k, params, query)

    async def queryElementById(self, id: str):
        return await self.request("queryElementById", id)

    async def queryElementRect(self, selector: str):
        return await self.request("queryElementRect", selector)

    async def quit(self):
        return await self.emit("quit")

    async def relaunch(self):
        return await self.emit("relaunch")

    async def replaceState(self, k: str, params: Optional[str], query: Optional[str]):
        return await self.request("replaceState", k, params, query)

    async def setFullScreen(self, fullScreen: bool):
        return await self.request("setFullScreen", fullScreen)

    async def setLeftSidebarVisible(self, visible: bool):
        return await self.request("setLeftSidebarVisible", visible)

    async def setRightSidebarVisible(self, visible: bool):
        return await self.request("setRightSidebarVisible", visible)
    
    async def setZoomFactor(self, factor: float):
        return await self.request("setZoomFactor", factor)

    async def showMsg(
        self, content: str, status: str = "success", key: Optional[str] = None, timeout: int = 3000
    ):
        """showMsg(content: string, status?: string, opts?: Partial<UIMsgOptions>): Promise<string>"""
        return await self.emit(
            "showMsg", content, status, **{"key": key, "timeout": timeout}
        )
