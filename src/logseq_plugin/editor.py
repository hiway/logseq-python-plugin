from datetime import datetime
from pprint import pprint
from typing import Union

from box import Box

from .block import Block
from .utils import mkbox


class LogseqEditor(object):
    def __init__(self, plugin):
        self._plugin = plugin
        self._command_handlers = {}
        self._command_palette = {}
        self._context_menu_item = {}
        self._input_selection_handler = None

    async def _register_handlers(self):
        if self._input_selection_handler:
            self._plugin.sio.on(
                "logseq.Editor.onInputSelectionEnd", self._input_selection_handler
            )

        for command, func in self._command_handlers.items():
            event_name = f"slash-command-{command.replace('/', '')}"
            await self._plugin.emit(
                "logseq.Editor.registerSlashCommand", (command, event_name)
            )
            self._plugin.sio.on(event_name, func)

        for label, data in self._command_palette.items():
            event_name = f"command-palette-{label}"
            await self._plugin.emit(
                "logseq.Editor.registerCommandPalette",
                (label, data["shortcut"], event_name),
            )
            self._plugin.sio.on(event_name, data["handler"])

        for item_name, func in self._context_menu_item.items():
            event_name = f"context-menu-item-{item_name}"
            await self._plugin.emit(
                "logseq.Editor.registerBlockContextMenuItem", (item_name, event_name)
            )
            self._plugin.sio.on(event_name, func)

    def registerSlashCommand(self, command: str):
        def outer(func):
            async def async_inner(_sid, *args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self._command_handlers.update({command: async_inner})
            return async_inner

        return outer

    def registerCommandPalette(self, label: str, shortcut: str):
        def outer(func):
            async def async_inner(_sid, *args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self._command_palette.update(
                {label: {"shortcut": shortcut, "handler": async_inner}}
            )
            return async_inner

        return outer

    def registerBlockContextMenuItem(self, item_name: str):
        def outer(func):
            async def async_inner(_sid, *args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self._context_menu_item.update({item_name: async_inner})
            return async_inner

        return outer

    def onInputSelectionEnd(self):
        def outer(func):
            async def async_inner(_sid, *args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self._input_selection_handler = async_inner
            return async_inner

        return outer

    async def insertAtEditingCursor(self, content: str):
        await self._plugin.emit("logseq.Editor.insertAtEditingCursor", content)

    async def getCurrentBlock(self):
        return Box(await self._plugin.request("logseq.Editor.getCurrentBlock"))

    async def getEditingBlockContent(self):
        return await self._plugin.request("logseq.Editor.getEditingBlockContent")

    async def getPage(self, page_name: str):
        return await self._plugin.request("logseq.Editor.getPage", page_name)

    async def getBlock(self, srcBlock: str, includeChildren: bool = False):
        return await self._plugin.request(
            "logseq.Editor.getBlock",
            dict(srcBlock=srcBlock, includeChildren=includeChildren),
        )

    async def openInRightSidebar(self, uuid: str):
        return await self._plugin.emit("logseq.Editor.openInRightSidebar", uuid)

    async def updateBlock(
        self,
        srcBlock: str,
        content: str,
        before: bool = False,
        sibling: bool = False,
        isPageBlock: bool = False,
        properties: Union[dict, None] = None,
    ):
        return await self._plugin.request(
            "logseq.Editor.updateBlock",
            {
                "srcBlock": srcBlock,
                "content": content,
                "properties": properties,
                "before": before,
                "sibling": sibling,
                "isPageBlock": isPageBlock,
            },
        )

    async def upsertBlockProperty(self, block: Block, key: str, value: str):
        return await self._plugin.emit(
            "logseq.Editor.upsertBlockProperty", (block, key, value)
        )

    async def getPageBlocksTree(self, page_name: str):
        return await self._plugin.request("logseq.Editor.getPageBlocksTree", page_name)

    async def insertBlock(
        self,
        srcBlock: str,
        content: str,
        before: bool = False,
        sibling: bool = False,
        isPageBlock: bool = False,
        properties: Union[dict, None] = None,
    ):
        return await self._plugin.request(
            "logseq.Editor.insertBlock",
            {
                "srcBlock": srcBlock,
                "content": content,
                "properties": properties,
                "before": before,
                "sibling": sibling,
                "isPageBlock": isPageBlock,
            },
        )

    async def appendBlockToJournalInbox(self, inboxName: str, block: Block):
        today = datetime.now().strftime("%Y%m%d")
        result = await self._plugin.DB.datascriptQuery(
            f"""
        [:find (pull ?p [*])
         :where
         [?b :block/page ?p]
         [?p :block/journal? true]
         [?p :block/journal-day ?d]
         [(= ?d {today})]]
         """
        )
        result = sum(result, [])
        if len(result) == 0:
            raise Exception("No journal page found")
        page_name = result[0]["name"]
        page_blocks_tree = await self.getPageBlocksTree(page_name)
        inboxBlock = None
        if not inboxName:
            inboxBlock = page_blocks_tree[0]
        for block_ in page_blocks_tree:
            if block_.content == inboxName:
                inboxBlock = block_
        if not inboxBlock:
            before = page_blocks_tree[0].content is not ""
            inboxBlock = await self.insertBlock(
                page_blocks_tree[0].uuid, inboxName, sibling=True, before=before
            )
        inboxBlockTree = await self.getBlock(inboxBlock.uuid, True)
        targetBlock = None
        if inboxBlockTree.children:
            targetBlock = inboxBlockTree.children[-1]
            await self.insertBlock(
                targetBlock.uuid,
                content=block.content,
                properties=block.properties,
                sibling=True,
            )
        else:
            targetBlock = inboxBlockTree
            await self.insertBlock(
                targetBlock.uuid,
                content=block.content,
                properties=block.properties,
                sibling=False,
            )
