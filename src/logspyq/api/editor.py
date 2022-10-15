from logspyq.api.proxy import LogseqProxy


class Editor(LogseqProxy):
    def registerSlashCommand(self, command: str):
        def decorator(func):
            event_name = f"slash-command-{command.replace('/', '')}"
            self.register_callback(
                "registerSlashCommand", 
                    event_name=event_name,
                    command=command,
                    func=func
            )
            return func

        return decorator

    def registerBlockContextMenuItem(self, tag: str):
        def decorator(func):
            self.register_callback(
                "registerBlockContextMenuItem", 
                    event_name=f"block-context-menu-item-{tag}",
                    tag=tag,
                    func=func
            )
            return func

        return decorator

    def onInputSelectionEnd(self):
        def decorator(func):
            self.register_callback(
                "onInputSelectionEnd", 
                    event_name="input-selection-end",
                    func=func
            )
            return func

        return decorator

    async def appendBlockInPage(self, page: str, content: str, **opts):
        return await self.request("appendBlockInPage", page, content, **opts)

    async def insertAtEditingCursor(self, text: str):
        await self.emit("insertAtEditingCursor", text)

    async def getCurrentBlock(self):
        return await self.request("getCurrentBlock")

    async def getCurrentPage(self):
        return await self.request("getCurrentPage")

    async def getEditingBlockContent(self):
        return await self.request("getEditingBlockContent")

    async def insertBlock(self, srcBlk: str, content: str, sibling=True, isPageBlock=False, before=False, **opts):
        opts["sibling"] = sibling
        opts["isPageBlock"] = isPageBlock
        opts["before"] = before
        return await self.request("insertBlock", srcBlk, content, **opts)

    async def exitEditingMode(self, selectBlock: bool = False):
        await self.emit("exitEditingMode", selectBlock)
