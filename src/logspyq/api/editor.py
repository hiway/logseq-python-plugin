from datetime import datetime
from box import Box
from typing import Optional, List
from logspyq.api.proxy import LogseqProxy
from .utils import mkbox

class Editor(LogseqProxy):
    def registerSlashCommand(self, command: str):
        def decorator(func):
            event_name = f"slash-command-{command.replace('/', '')}"

            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "registerSlashCommand",
                event_name=event_name,
                command=command,
                func=_async_inner,
            )
            return _async_inner

        return decorator

    def registerBlockContextMenuItem(self, tag: str):
        def decorator(func):
            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "registerBlockContextMenuItem",
                event_name=f"block-context-menu-item-{tag}",
                tag=tag,
                func=_async_inner,
            )
            return _async_inner

        return decorator

    def onInputSelectionEnd(self):
        def decorator(func):
            async def _async_inner(*args):
                args = [mkbox(a) for a in args]
                return await func(*args)

            self.register_callback(
                "onInputSelectionEnd", event_name="input-selection-end", func=_async_inner
            )
            return _async_inner

        return decorator

    async def appendBlockInPage(self, page: str, content: str, **opts):
        return await self.request("appendBlockInPage", page, content, **opts)

    async def checkEditing(self) -> bool:
        return await self.request("checkEditing")

    async def createPage(
        self,
        pageName: str,
        createFirstBlock: bool = False,
        format: str = "markdown",
        journal: bool = False,
        redirect: bool = False,
        **properties,
    ):
        """
        Create a new page.

        createPage(
            pageName: string,
            properties?: {},
            opts?: Partial<{
                createFirstBlock: boolean;
                format: "markdown" | "org";
                journal: boolean;
                redirect: boolean
                }>): Promise<PageEntity>
        """
        opts = {
            "createFirstBlock": createFirstBlock,
            "format": format,
            "journal": journal,
            "redirect": redirect,
        }
        return await self.request("createPage", pageName, properties, **opts)

    async def deletePage(self, page: str):
        await self.emit("deletePage", page)

    async def editBlock(self, srcBlock: str, pos: Optional[int] = None):
        """
        Edit a block.

        editBlock(srcBlock: BlockIdentity, opts?: { pos: number }): Promise<void>
        """
        if pos:
            await self.emit("editBlock", srcBlock, {"pos": pos})
        else:
            await self.emit("editBlock", srcBlock)

    async def exitEditingMode(self, selectBlock: bool = False):
        await self.emit("exitEditingMode", selectBlock)

    async def getAllPages(self, repo: Optional[str] = None) -> List[Box]:
        if repo:
            return await self.request("getAllPages", {"repo": repo})
        else:
            return await self.request("getAllPages")
    
    async def getBlock(self, srcBlock: str, includeChildren: bool = False) -> Box:
        """
        getBlock(srcBlock: number | BlockIdentity, opts?: Partial<{ includeChildren: boolean }>)
        """
        return await self.request("getBlock", srcBlock, {"includeChildren": includeChildren})

    async def getBlockProperties(self, block: str) -> Box:
        return await self.request("getBlockProperties", block)
    
    async def getBlockProperty(self, block: str, key: str) -> str:
        return await self.request("getBlockProperty", block, key)

    async def getCurrentBlock(self) -> Box:
        return await self.request("getCurrentBlock")

    async def getCurrentPage(self) -> Box:
        return await self.request("getCurrentPage")
    
    async def getCurrentPageBlocksTree(self) -> Box:
        return await self.request("getCurrentPageBlocksTree")

    async def getEditingBlockContent(self) -> str:
        return str(await self.request("getEditingBlockContent"))

    async def getEditingCursorPosition(self) -> Box:
        return await self.request("getEditingCursorPosition")

    async def getNextSiblingBlock(self, srcBlock: str) -> Box:
        return await self.request("getNextSiblingBlock", srcBlock)
    
    async def getPage(self, srcPage: str, includeChildren: bool = False) -> Box:
        return await self.request("getPage", srcPage, {"includeChildren": includeChildren})

    async def getPageBlocksTree(self, page: str) -> Box:
        return await self.request("getPageBlocksTree", page)
    
    async def getPageLinkedReferences(self, page: str) -> Box:
        return await self.request("getPageLinkedReferences", page)

    async def getPagesFromNamespace(self, namespace: str) -> Box:
        return await self.request("getPagesFromNamespace", namespace)

    async def getPagesTreeFromNamespace(self, namespace: str) -> Box:
        return await self.request("getPagesTreeFromNamespace", namespace)

    async def getPreviousSiblingBlock(self, srcBlock: str) -> Box:
        return await self.request("getPreviousSiblingBlock", srcBlock)
    
    async def getSelectedBlocks(self) -> Box:
        return await self.request("getSelectedBlocks")

    async def insertAtEditingCursor(self, text: str):
        await self.emit("insertAtEditingCursor", text)

    async def insertBatchBlock(self, srcBlock: str, batch: list, before: bool = False, sibling: bool = True):
        opts = {}
        if before:
            opts.update({"before": before})
        if sibling:
            opts.update({"sibling": sibling})
        return await self.request("insertBatchBlock", srcBlock, batch, opts)

    async def insertBlock(
        self,
        srcBlk: str,
        content: str,
        sibling=True,
        isPageBlock=False,
        before=False,
        **opts,
    ) -> Box:
        opts["sibling"] = sibling
        opts["isPageBlock"] = isPageBlock
        opts["before"] = before
        return await self.request("insertBlock", srcBlk, content, **opts)

    async def moveBlock(self, srcBlock: str, targetBlock: str, before: bool = False, children: bool = False):
        opts = {}
        if before:
            opts.update({"before": before})
        if children:
            opts.update({"children": children})
        await self.emit("moveBlock", srcBlock, targetBlock, opts)
    
    async def openInRightSidebar(self, uuid: str):
        await self.emit("openInRightSidebar", uuid)
    
    async def prependBlockInPage(self, page: str, content: str, **opts) -> Box:
        return await self.request("prependBlockInPage", page, content, **opts)
    
    async def removeBlock(self, srcBlock: str):
        await self.emit("removeBlock", srcBlock)
    
    async def removeBlockProperty(self, block: str, key: str):
        await self.emit("removeBlockProperty", block, key)
    
    async def renamePage(self, oldName: str, newName: str):
        await self.emit("renamePage", oldName, newName)
    
    async def restoreEditingCursor(self):
        await self.emit("restoreEditingCursor")
    
    async def scrollToBlockInPage(self, pageName: str, blockId: str, replace_state: bool = False):
        await self.emit("scrollToBlockInPage", pageName, blockId, {"replace_state": replace_state})
    
    async def setBlockCollapsed(self, uuid: str, collapsed: bool = True, toggle: bool = False):
        opts = {}
        if collapsed:
            opts.update({"collapsed": collapsed})
        if toggle:
            opts.update({"collapsed": "toggle"})
        await self.emit("setBlockCollapsed", uuid, opts)
    
    async def updateBlock(self, srcBlock: str, content: str, **properties):
        await self.emit("updateBlock", srcBlock, content, {"properties": properties})

    async def appendBlockToJournalInbox(self, inboxName: str, block: Box):
        today = datetime.now().strftime("%Y%m%d")
        result = await self.logseq.DB.datascriptQuery(
            f"""
        [:find (pull ?p [*])
         :where
         [?b :block/page ?p]
         [?p :block/journal? true]
         [?p :block/journal-day ?d]
         [(= ?d {today})]]
         """.strip().replace("\n", " ").replace("  ", " ")
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
            before = page_blocks_tree[0].content != ""
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
                properties=block.properties if "properties" in block else {},
                sibling=True,
            )
        else:
            targetBlock = inboxBlockTree
            await self.insertBlock(
                targetBlock.uuid,
                content=block.content,
                properties=block.properties if "properties" in block else {},
                sibling=False,
            )
