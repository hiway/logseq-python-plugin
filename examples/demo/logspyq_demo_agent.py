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
async def input_demo(sid, event):
    # await logseq.Editor.deletePage("BOING")
    # await logseq.Editor.appendBlockInPage("BOING", "Demo, World!")
    # await logseq.Editor.insertAtEditingCursor("[[BOING]]")
    # b = await logseq.Editor.getCurrentBlock()
    # await logseq.Editor.updateBlock(b.uuid, "YOU CALLED?")
    # await logseq.Editor.scrollToBlockInPage("Scrapbook", "634ac67f-f8ab-4e19-b755-272cda30a490")
    # print("input_demo", sid, event.text)
    await logseq.UI.showMsg("Demo, World!", "success", timeout=5000)


@logseq.Editor.registerSlashCommand("appendBlockInPage")
async def appendBlockInPage(sid):
    # !! This does not work when in Journal mode
    page = await logseq.Editor.getCurrentPage()
    await logseq.Editor.appendBlockInPage(page.uuid, "Demo: appendBlockInPage")

# @logseq.on_interval(seconds=5)
# async def check_editing():
#     editing = await logseq.Editor.checkEditing()
#     if editing:
#         logseq.log.info(f"Editing: {editing}")
#     else:
#         logseq.log.info("Not editing")


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484)
