from logspyq.api import LSPluginUser

logseq = LSPluginUser()


@logseq.Editor.registerSlashCommand("demo")
async def slash_demo(sid):
    await logseq.Editor.insertAtEditingCursor("Demo, World!")


@logseq.Editor.registerBlockContextMenuItem("demo")
async def block_demo(sid):
    cb = await logseq.Editor.getCurrentBlock()
    await logseq.Editor.insertBlock(cb.uuid, "Demo, World!", sibling=True)


@logseq.Editor.onInputSelectionEnd()
async def input_demo(sid):
    await logseq.Editor.insertAtEditingCursor("BOO!")


@logseq.Editor.registerSlashCommand("appendBlockInPage")
async def appendBlockInPage(sid):
    # !! This does not work when in Journal mode
    page = await logseq.Editor.getCurrentPage()
    await logseq.Editor.appendBlockInPage(page.uuid, "Demo: appendBlockInPage")


if __name__ == "__main__":
    logseq.run(host="localhost", port=3000)
