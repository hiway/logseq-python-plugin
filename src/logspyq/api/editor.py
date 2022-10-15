from logspyq.api.proxy import LogseqProxy


class Editor(LogseqProxy):
    def registerSlashCommand(self, command: str):
        def decorator(func):
            event_name = f"slash-command-{command.replace('/', '')}"
            self.register_callback(
                "Editor.registerSlashCommand", 
                    event_name=event_name,
                    command=command,
                    func=func
            )
            return func

        return decorator

    async def insertAtEditingCursor(self, text: str):
        await self.logseq.emit("Editor.insertAtEditingCursor", text)

    async def getCurrentBlock(self):
        return await self.logseq.request("Editor.getCurrentBlock")

    async def insertBlock(self, srcBlk: str, content: str, sibling=True, isPageBlock=False, before=False, **opts):
        opts["sibling"] = sibling
        opts["isPageBlock"] = isPageBlock
        opts["before"] = before
        return await self.logseq.request("Editor.insertBlock", srcBlk, content, **opts)

    async def exitEditingMode(self, selectBlock: bool = False):
        await self.logseq.emit("Editor.exitEditingMode", selectBlock)
