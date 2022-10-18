from logspyq.api import LogseqPlugin

logseq = LogseqPlugin(name="Demo Agent", description="Demo Agent")


# @logseq.Editor.registerSlashCommand("demo")
# async def slash_demo(sid):
#     await logseq.Editor.insertAtEditingCursor("Demo, World!")


# @logseq.Editor.registerBlockContextMenuItem("demo")
# async def block_demo(sid):
#     cb = await logseq.Editor.getCurrentBlock()
#     await logseq.Editor.insertBlock(cb.uuid, "Demo, World!", sibling=True)


# @logseq.Editor.onInputSelectionEnd()
# async def input_demo(sid, event):
#     await logseq.Editor.deletePage("BOING")
#     await logseq.Editor.appendBlockInPage("BOING", "Demo, World!")
#     await logseq.Editor.insertAtEditingCursor("[[BOING]]")
#     b = await logseq.Editor.getCurrentBlock()
#     await logseq.Editor.updateBlock(b.uuid, "YOU CALLED?")
#     await logseq.App.showMsg("Demo, World!", "success", timeout=5000)
#     print("input_demo", sid, event.text)


# @logseq.Editor.registerSlashCommand("appendBlockInPage")
# async def appendBlockInPage(sid):
#     # !! This does not work when in Journal mode
#     page = await logseq.Editor.getCurrentPage()
#     await logseq.Editor.appendBlockInPage(page.uuid, "Demo: appendBlockInPage")

# @logseq.App.onCurrentGraphChanged()
# async def onCurrentGraphChanged(sid, event):
#     print("onCurrentGraphChanged", sid, event)

# @logseq.on_interval(seconds=5)
# async def check_editing():
#     editing = await logseq.Editor.checkEditing()
#     if editing:
#         logseq.log.info(f"Editing: {editing}")
#     else:
#         logseq.log.info("Not editing")

# @logseq.App.onMacroRendererSlotted()
# async def fancy_block(sid, event):
#     """
#     {{renderer :hello, World}}
#     """
#     t = event.arguments[0]
#     if t != ":hello":
#         print("block not :hello...", t)
#         return
#     name = event.arguments[1]
#     await logseq.provideUI(
#         key="h1-playground",
#         slot=event.slot,
#         template=f"""
#         <h2 style="color: red">Hello {name}!</h2>
#         """,
#     )

# @logseq.App.onRouteChanged()
# async def route_changed(sid, event):
#     print("route_changed", sid, event)
#     status = await logseq.App.execGitCommand("status")
#     print("git status", status)


# @logseq.App.registerCommand("demo") ## ??? doesn't work
# async def demo(sid, event):
#     await logseq.Editor.insertAtEditingCursor("Demo, World!")

@logseq.App.registerCommandPalette("demo", binding="ctrl+shift+t", label="Demo")
async def shortcut_demo(sid, event):
    await logseq.Editor.insertAtEditingCursor("Demo, World!")
    print("shortcut_demo", sid, event)


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484)
